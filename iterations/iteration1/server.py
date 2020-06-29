from flask import Flask
from functions import CSV
app = Flask(__name__)
app.config["SECRET_KEY"] = "Highly secret key"

#global variables
usersCSV = CSV("csv/users.csv")
qaaCSV = CSV("csv/qaa.csv")
coursesCSV = CSV("csv/courses.csv")
surveyCSV = CSV("csv/surveys.csv")
user_authenticated = False	
