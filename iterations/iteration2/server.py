from flask import Flask
from users import User, Guest
from fileReader import CSVReader
from fileWriter import CSVWriter
app = Flask(__name__)
app.config["SECRET_KEY"] = "Highly secret key"

#global variables
user = Guest()
usersCSVReader = CSVReader("csv/passwords.csv")
usersCSVWriter = CSVWriter("csv/passwords.csv")
qaaCSVReader = CSVReader("csv/questionpool.csv")
qaaCSVWriter = CSVWriter("csv/questionpool.csv")
coursesCSVReader = CSVReader("csv/courses.csv")
coursesCSVWriter = CSVWriter("csv/courses.csv")
enrolmentsCSVReader = CSVReader("csv/enrolments.csv")
respondentsCSVReader = CSVReader("csv/respondents.csv")
respondentsCSVWriter = CSVWriter("csv/respondents.csv")
