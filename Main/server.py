from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
import prediction
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# MongoDB connection
uri = ""
client = MongoClient(uri)
db = client["crimedb"]
collection = db["reports"]
users = db["admin"]

app.mount("/static", StaticFiles(directory="."), name="static")
#request to store report
@app.post("/report")
def report(data: dict):
    collection.insert_one({
        "time": datetime.now(),
        "location": {
            "area": data["location"],
            "lat": data["lat"],
            "lon": data["lon"]
        },
        "crime_type": data["crime_type"],
        "description": data["description"]
    })
    return {"status": "ok"}

#request to run hawkes model and retrieve heatmap genrated
@app.get("/predict")
def predict():
    file_path = prediction.predict_db(collection)

    return JSONResponse({
        "url": f"http://172.16.6.71:8000/static/{file_path}"
    })

#request for user to sign up
@app.post("/signup")
def signup(data: dict):
    existing = users.find_one({"username": data["username"]})

    if existing:
        return {"status": "error"}

    users.insert_one({
        "account_creation": datetime.now(),
        "username": data["username"],
        "password": data["password"]
    })

    return {"status": "ok"}

#request for user to log in
@app.post("/login")
def login(data: dict):
    user = users.find_one({"username": data["username"]})

    if not user:
        return {"status": "error"}

    if user["password"] == data["password"]:
        return {"status": "ok"}

    return {"status": "error"}
