"""
File: server.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file contains the functions to create a database and
             store the survey information.
"""

# Imported libraries...
from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import csv

engine = create_engine('sqlite:///data.db')
Base = declarative_base()
DBSession = sessionmaker(bind=engine)


from users import User, Admin, Staff, Student, Guest, Unassigned

app = Flask(__name__)
app.config["SECRET_KEY"] = "Highly secret key"

# Global variables...
user = Unassigned()


# This function is used to create a database and store all of the survey's information.
def createDatabases():
    import question
    import users
    import courses
    import survey
    Base.metadata.create_all(engine)

    # Load all the usernames and passwords from the csv file to the database.
    firstRun = 0
    with open('csv/passwords.csv', 'r') as csv_in:
        session = DBSession()
        if (session.query(User).first() == None):
            print("Loading default passwords")

            firstRun = 1
            reader = csv.reader(csv_in)
            for row in reader:
                u = User()
                u.username = row[0]
                u.password = row[1]
                u.role = row[2]
                u.courses = []
                u.surveysResponded = []
                if (u.role == "guest"):
                   u.authenticated = True 
                else:
                   u.authenticated = False
                session.add(u)
            session.commit()
        session.close()

    # Load all the enrolments from the csv file to the database.
    with open('csv/enrolments.csv', 'r') as enrol:
        if (firstRun == 1):
            session = DBSession()
            reader2 = csv.reader(enrol)
            print("Loading default enrolments")

            last = '-1'
            lastU = None
            for rowa in reader2:
                if(rowa[0] != last):
                    lastU = session.query(User).filter(User.username == rowa[0]).first()
                    session.add(lastU)
                    last = lastU.username
                temp = list(lastU.courses)
                temp.append(rowa[1] + ", " + rowa[2])
                lastU.courses=temp

            print("loaded...")
            session.commit()
            session.close()
            firstRun = 2

    # Load all the courses and their details from the csv file to the database.
    with open('csv/courses.csv', 'r') as csv_in:
        session = DBSession()
        if(session.query(courses.SessionOffering).first() == None):
            print("Loading default courses")
            reader = csv.reader(csv_in)
            for row in reader:
                c = courses.SessionOffering()
                c.session = row[0] + ", " + row[1]
                session.add(c)
            session.commit()
        session.close()

createDatabases()
