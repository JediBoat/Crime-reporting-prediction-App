import kivy
from kivy.app import App 
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import requests
import threading
import webbrowser

class MainWindow(Screen):
    pass

class LocationWindow(Screen):
    pass

class AddressWindow(Screen):
    pass

class TransportWindow(Screen):
    pass

class CyberReportWindow(Screen):
    pass

class ViolentWindow(Screen):
    pass

class PropertyWindow(Screen):
    pass

class SexualWindow(Screen):
    pass

class DrugWindow(Screen):
    pass

class PublicOrderWindow(Screen):
    pass

class FraudWindow(Screen):
    pass

class CyberWindow(Screen):
    pass

class WhiteCollarWindow(Screen):
    pass

class OrganisedCrimeWindow(Screen):
    pass

class LoginWindow(Screen):
    pass

class SignUpWindow(Screen):
    pass

class PredictWindow(Screen):

    def on_enter(self):
        threading.Thread(target=self.run_prediction, daemon=True).start()
    #When the user logs in it send a request to run model and view a heatmap
    def run_prediction(self):
        try:
            response = requests.get("https://reporter-app-backend.onrender.com/predict")
            data = response.json()
            webbrowser.open(data["url"])

        except Exception as e:
            print("Error:", e)


class ConfirmationWindow(Screen):
    #stores the crime report when the user enters  the page
    def on_enter(self):
        self.store(self.manager.loc_input, self.manager.lat, self.manager.lon)

    #sends the data to be stored by the database
    def store(self,location, lat, lon):
        try:
            requests.post("https://reporter-app-backend.onrender.com/report", json={
                "location": location,
                "lat": lat,
                "lon": lon,
                "crime_type": self.manager.current_report,
                "description": self.manager.desc_input
            })
            print("Sent to server")

        except Exception as e:
            print("Error sending:", e)

class WindowManager(ScreenManager):
    past_screens = []
    past_screens.append("main")
    current_report = ""
    switch = False
    loc_input = ""
    desc_input = ""
    lat = 0
    lon = 0
    #changes screenn
    def screen_change(self, screen_name):
        if self.current:
            self.past_screens.append(self.current)
        self.current = screen_name
    #goes back to previous screen
    def go_back(self):
        if self.past_screens:
            self.current = self.past_screens.pop()
        else:
            self.current = "main"
            self.past_screens.append("main")
    #stores  the crime name for what the user is reporting
    def confim_crime(self, button):
        self.current_report = button.text
    #checks if the location are valid
    def geo_input(self, textinput, label, descinput):
        
        location =  self.geocode_address(textinput.text)
        self.desc_input = descinput.text

        if(location != None):
            self.loc_input = textinput.text
            self.lat, self.lon = location
            self.screen_change("confirmation")
            label.opacity = 0
            textinput.text = ""
            descinput.text = ""
        else:
            label.opacity = 1
            textinput.text = ""

    #adds user to the database
    def add_user(self, userinput, passinput):
        try:
            response = requests.post("https://reporter-app-backend.onrender.com/signup", json={
                "username": userinput.text,
                "password": passinput.text
            })

            data = response.json()

            if data["status"] == "ok":
                print("User created")
                self.screen_change("login")
            else:
                print("User already exists")

        except Exception as e:
            print("Error:", e)

    #logs user in by send request to the server    
    def log_in(self, userinput, passinput, label):
        try:
            response = requests.post("https://reporter-app-backend.onrender.com/login", json={
                "username": userinput.text,
                "password": passinput.text
            })

            data = response.json()

            if data["status"] == "ok":
                label.opacity = 0
                userinput.text = ""
                passinput.text = ""
                self.screen_change("predict")
            else:
                label.opacity = 1

        except Exception as e:
            print("Error:", e)

    #checks if location is valid if so retrieves lat and long
    def geocode_address(self, address):
        url = "https://nominatim.openstreetmap.org/search"
        headers = {
            "User-Agent": "reporter"
        }

        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print("Geocode failed:", response.status_code)
            return None

        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])

        return None


kv = Builder.load_file("main.kv")


class mainApp(App):
    def build(self):#builds the app
        return kv
    
if __name__ == "__main__":
    mainApp().run()