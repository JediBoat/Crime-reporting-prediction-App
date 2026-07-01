from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from scipy.optimize import minimize

#gives crimes weights
def get_weight(row):
    return row.get("weight", 1.0)

#used to optimize parameters
def log_likelihood(params, df):
    mu, alpha, beta, omega = params

    df = df.sort_values("time").reset_index(drop=True)
    logL = 0

    for i in range(len(df)):

        t_i = df.loc[i, "time"]
        lat_i = df.loc[i, "lat"]
        lon_i = df.loc[i, "lon"]

        intensity = mu

        for j in range(i):

            t_j = df.loc[j, "time"]
            dt = (t_i - t_j).total_seconds() / 3600
            d = haversine(lat_i, lon_i, df.loc[j, "lat"], df.loc[j, "lon"])
            w = get_weight(df.loc[j])
            intensity += alpha * w * np.exp(-omega * dt) * np.exp(-beta * d)
        logL += np.log(intensity + 1e-9)

    T = (df["time"].max() - df["time"].min()).total_seconds() / 3600
    area = (df["lat"].max() - df["lat"].min()) * (df["lon"].max() - df["lon"].min())
    integral = mu * T * area

    return logL - integral

#Calculates the distance between 2 points
def haversine(lat1, lon1, lat2, lon2):
        R = 6371 

        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c

#Calculates the risk of crime in an area
def intensity(group, current_time, lat, lon, mu, alpha, beta, omega):

    intensity = mu

    for _, row in group.iterrows():

        dt = (current_time - row["time"]).total_seconds() / 3600

        if dt > 0:

            d = haversine(lat, lon, row["lat"], row["lon"])
            w = get_weight(row)

            intensity += alpha * w * np.exp(-omega * dt) * np.exp(-beta * d)

    return intensity

#uses to optimize model parameters
def fit_mle(df):

    initial = [0.1, 0.5, 1.0, 0.01]

    bounds = [
        (1e-5, None),
        (1e-5, None),
        (1e-5, None),
        (1e-5, None)
    ]

    result = minimize(
        lambda p: -log_likelihood(p, df),
        initial,
        method="L-BFGS-B",
        bounds=bounds
    )

    return {
        "mu": result.x[0],
        "alpha": result.x[1],
        "beta": result.x[2],
        "omega": result.x[3],
        "success": result.success
    }

#uses database data to calculates the risk of crime in area around where the crime occurred
def predict_db(collection):
    data = list(collection.find())
    print("Loaded:", len(data))

    cleaned = []

    for crime in data:
        try:
            cleaned.append({
                "time": pd.to_datetime(crime["time"]),
                "lat": float(crime["location"]["lat"]),
                "lon": float(crime["location"]["lon"]),
                "area": crime["location"]["area"],
                "crime_type": crime["crime_type"]
            })
        except:
            continue  # skip bad records

    df = pd.DataFrame(cleaned)
    df = df.sort_values("time").reset_index(drop=True)
    params = fit_mle(df)

    lat_min, lat_max = 49.8, 58.7
    lon_min, lon_max = -8.5, 2.2

    n_points = 800

    locations = np.column_stack([
        np.random.uniform(lat_min, lat_max, n_points),
        np.random.uniform(lon_min, lon_max, n_points)
    ])

    mu = params["mu"]
    alpha = params["alpha"]
    beta = params["beta"]
    omega = params["omega"]

    crime_groups = df.groupby("crime_type")
    current_time = df["time"].max()

    results = []

    for crime_type, group in crime_groups:
        for lat, lon in locations:
            risk = intensity(group, current_time, lat, lon, mu, alpha, beta, omega)

            results.append({
                "crime_type": crime_type,
                "lat": lat,
                "lon": lon,
                "risk": float(risk)
            })
    
    for crime_type in df["crime_type"].unique():
        values = [r["risk"] for r in results if r["crime_type"] == crime_type]

        min_v = min(values)
        max_v = max(values)

        for r in results:
            if r["crime_type"] == crime_type:
                r["risk_percent"] = ((r["risk"] - min_v) / (max_v - min_v + 1e-9)) * 100

                if r["risk_percent"] > 70:
                    r["level"] = "High"
                elif r["risk_percent"] > 30:
                    r["level"] = "Medium"
                else:
                    r["level"] = "Low"

    #creating the heatmap
    m = folium.Map(location=[53.48, -2.24], zoom_start=6)
    #Setting up layers for each crime type
    for crime_type in df["crime_type"].unique():

        layer = folium.FeatureGroup(
            name=crime_type,
            show=(crime_type == "violent-crime")
        )

        heat_data = []
        #this maps the data taken from previously recorded crimes
        real_points = df[df["crime_type"] == crime_type]
        for _, row in real_points.iterrows():

            heat_data.append([row["lat"], row["lon"], 1])

            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=6,
                popup=f"""
                Crime: {crime_type}<br>
                Source: Real Data
                """,
                color="blue",
                fill=True,
                fill_opacity=0.6
            ).add_to(layer)

        #this maps predicted crimes
        for r in results:
            if r["crime_type"] == crime_type:

                heat_data.append([r["lat"], r["lon"], r["risk_percent"]])

                folium.CircleMarker(
                    location=[r["lat"], r["lon"]],
                    radius=10,
                    popup=f"""
                    Crime: {r['crime_type']}<br>
                    Risk: {r['risk_percent']:.1f}%<br>
                    Level: {r['level']}
                    """,
                    color=(
                        "red" if r["level"] == "High" else
                        "orange" if r["level"] == "Medium" else
                        "green"
                    ),
                    fill=True,
                    fill_opacity=0.7
                ).add_to(layer)

        #establishing heatmap and adding layers
        HeatMap(
            heat_data,
            radius=100,
            blur=15,
            min_opacity=0.3
        ).add_to(layer)

        layer.add_to(m)
        
    folium.LayerControl(collapsed=False).add_to(m)
    #saved and opened
    m.save("predicted_crime_heatmap.html")
    return "predicted_crime_heatmap.html"