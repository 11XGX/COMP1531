"""
File: users.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file contains the class of a user and defines their information of:
             course offerings, permissions and whether they have responded to a survey.
"""

# Imported libraries...
from abc import ABCMeta, abstractmethod
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from server import Base
from courses import SessionOffering
from list import Json
import server

# This class defines the attributes and behaviour of a user including their information, course offerings,
# permissions and whether they have responded to a survey.
class User(Base):
    __metaclass__ = ABCMeta
    __tablename__ = 'USERS'
    username = Column(String(250), primary_key=True)
    password = Column(String(250))
    # List of session offerings.
    courses = Column(Json(500), default = [])
    role = Column(String(250))
    # List of survey keys.
    surveysResponded = Column(Json(500), default = [])
    authenticated = Column(Boolean)

    # This function obtains all the courses currently being offered and returns them in the form of a list.
    def getCourses(self):
        if (self.courses == None):
            return []
        courses = []
        for c in self.courses:
            courses.append(getCourseFromName(c))        
        return courses
    
    # OCP. Extended users must have permissions defined.
    # This function designates the permissions of a user (based on their role) and restricts their access
    # to the survey system accordingly.
    @abstractmethod
    def getPermissions(self):
        return {}


    # This function checks if a specific user has completed a specific survey by searching through respondents
    def hasRespondedSurvey(self, surveyKey):
        return surveyKey in self.surveysResponded

    # This function appends a user's response to the survey's list of responses.
    def hasRespondedSurveys(self, courses):
        responseRegistered = []
        for course in self.getCourses():
            if (course == None or course.getSurvey() == None):
                responseRegistered.append(-1)
                continue
            if course.getSurvey() != 0:
                responseRegistered.append(self.hasRespondedSurvey(course.getSurvey().key))
            else:
                responseRegistered.append(-1)
        return responseRegistered

      
    # This function checks if a specific user is allowed to access a survey with the given key.
    # It checks this by looking at the courses associated with the user object and if any of
    # those courses have a matching key to the survey.
    def userCanParticiplate(self, surveyKey):
        for course in self.getCourses():
            if (course.getSurvey() != None and course.getSurvey().key == surveyKey):
                return True
        return False

class Admin(User):
    role = "admin"
    def getPermissions(self):
        return {"dashboard" : ["createsurvey", "createquestions", "viewsurveys", "viewquestions", "enrolment"], "createsurvey" : [], "createquestions" : [], "viewsurveys" : ["editsurvey", "active", "delete", 1, 2, 3, "doform", "surveyresult"], "modifysurvey" : ["deletecompulsory", "deleteoptional", "addcompulsory", "addoptional", "undeletablequestions", 0, 1], "viewquestions" : [], "doform" : ["unlimited"], "surveyresult" : ["unlimited"], "enrolment" : []}   

class Staff(User):
    role = "staff"
    def getPermissions(self):
        return {"dashboard" : ["viewsurveys"], "viewsurveys" : ["editsurvey", 2, "surveyresult"], "modifysurvey" : ["deleteoptional", "addoptional", 1], "surveyresult" : [3]}

class Student(User):
    role = "student"
    def getPermissions(self):
        return {"dashboard" : ["viewsurveys"], "viewsurveys" : ["doform", "surveyresult"], "doform" : [], "surveyresult" : [3]}

class Guest(User):
    role = "guest"
    def getPermissions(self):
        return {"dashboard" : ["viewsurveys"], "viewsurveys" : ["doform", "surveyresult"], "doform" : [], "surveyresult" : [3]}

class Unassigned(User):
    role = "unassigned"
    def getPermissions(self):
        return {""}
    
# This function obtains a course and its details from a given key.
def getCourseFromName(key):
    session = server.DBSession()
    course = session.query(SessionOffering).filter(SessionOffering.session == key).first()
    session.close()
    return course

