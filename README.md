# Crime-reporting-prediction-App
The app allows civilians to report crimes, displays a heatmap of the incident locations, and predicts potential future instances of crime in nearby areas. 

Crime and Incident Reporting Mobile Application

A mobile application that enables users to report crimes while simultaneously generating real-time crime risk predictions using a Hawkes Process model. The system combines mobile reporting, a backend API, a NoSQL database, and predictive analytics to assist law enforcement in identifying emerging crime hotspots.

Overview

Traditional crime reporting methods often rely on phone calls or in-person visits, creating barriers for many members of the public. This project provides a digital alternative that simplifies crime reporting while collecting live data that can be analysed to identify areas with an increased risk of crime.

The system consists of:

Mobile application for submitting crime reports
Backend REST API
NoSQL database for storing reports and user accounts
Hawkes Process predictive model
Heatmap generation for crime risk visualisation

The project was developed as part of an MSc dissertation at Manchester Metropolitan University.

Features
Public Features
Submit crime reports
Enter crime type and description
Validate location using postcode lookup
Simple and accessible user interface
Police Features
Secure login
View generated crime risk heatmaps
Access prediction results
Backend Features
REST API communication
Crime report storage
User authentication
Predictive model execution
Automatic heatmap generation
System Architecture
Mobile Application
        │
        │ HTTP Requests
        ▼
Backend API Server
        │
 ┌──────┴────────┐
 │               │
 ▼               ▼
Database     Hawkes Process
                 │
                 ▼
          Heatmap Generator
                 │
                 ▼
        Heatmap displayed to users
Technologies Used
Mobile Application
Python
Kivy
Backend
Python
REST API
Database
NoSQL document database
Prediction Model
Hawkes Process
Maximum Likelihood Estimation (MLE)
Haversine Distance
Mapping
OpenStreetMap
Heatmap visualisation
Project Structure
project/
│
├── app/
│   ├── screens/
│   ├── widgets/
│   └── main.py
│
├── server/
│   ├── api.py
│   ├── routes.py
│   └── prediction.py
│
├── database/
│
├── model/
│   ├── hawkes.py
│   ├── heatmap.py
│   └── utils.py
│
├── assets/
│
├── requirements.txt
│
└── README.md
Installation

Clone the repository

git clone https://github.com/yourusername/crime-reporting-app.git

Move into the project

cd crime-reporting-app

Install dependencies

pip install -r requirements.txt

Run the backend server

python server.py

Run the mobile application

python main.py
How It Works
A user submits a crime report.
The report is validated and sent to the backend.
The backend stores the report in the database.
The Hawkes Process model analyses recent reports.
Crime risk scores are generated.
A heatmap is produced from the predictions.
Authorised users can view the generated heatmap.
Prediction Model

Unlike traditional hotspot mapping techniques that only display historical crime concentrations, this project uses a Hawkes Process model.

The model assumes that crime events can increase the likelihood of future nearby crimes for a period of time. As new reports are submitted, the prediction model updates crime risk estimates and produces a new heatmap.

API Endpoints
Method	Endpoint	Description
POST	/report	Submit a crime report
POST	/login	Authenticate user
GET	/predict	Run prediction model
GET	/heatmap	Retrieve generated heatmap
Testing

The system was evaluated using:

Black-box testing
Unit testing
Loop testing
Statement testing
Regression testing
AUC evaluation of the prediction model
Future Improvements
Real-time police integration
Push notifications
Stronger report validation
Improved predictive accuracy
Image and video evidence upload
Offline reporting support
Cross-platform deployment
Enhanced user authentication
Research

This project was completed as part of an MSc dissertation:
Mobile App Development for Crime and Incident Reporting
The research investigates how mobile reporting systems can be integrated with statistical prediction models to improve crime reporting accessibility while supporting proactive policing.


Disclaimer

This project was developed for research and educational purposes. It is not intended for operational law enforcement use without further validation, security improvements, and real-world testing.
