"""
File: question.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file contains a set of classes including the question handler and
             base question class, as well as individual MCQ and text question types.
"""

# Imported libraries...
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from server import Base, DBSession
from statistics import createPieChart, createTable
from list import Json
import server


# This class handles the basic functionalities of adding or deleting a question from a survey object.
class QuestionHandler(object):
    @staticmethod
    # This function creates a list of the question types ('MCQ' and 'Text Question').
    def getAllQuestionTypes():
        return ['MCQ', 'TextQuestion']

    @staticmethod
    # This function is used to delete a question from the survey database.
    def deleteQuestion(question):
        session = DBSession()
        q = session.query(Question).filter(question == Question.id).first()
        if (q != None):
            q.deleted = True
        session.commit()
        session.close()

    @staticmethod
    # This function creates a question based on the HTML Request Form coming from routes.py
    # It returns 0 oif the request is invalid or there is a system failure.
    def newQuestionRequest(key, questionType, request):
        compulsory = 1
        # If a question is optional, it should not be compulsory.
        if ("optional" in request.form):
            compulsory = 0
        # If a question is a text question, the survey should request a textual response from the user.
        if (questionType == "TextQuestion"):
            return TextQuestion(key, compulsory, request.form["question"])
        # If a question is a multiple choice question, the survey should request the user to select an
        # option from a list of given options.
        if (questionType == "MCQ"):
            responses = []
            for i in range(0, len(request.form)):
                if (str(i) in request.form and request.form[str(i)] != ""):
                    responses.append(request.form[str(i)])
            if (len(responses) > 0):
               return MCQ(key, compulsory, request.form["question"], responses)
        return 0

    @staticmethod
    def getChart(questionType, num, question, responses):
            chart = None
            if (questionType == "MCQ"):
                chart = createPieChart(str(num), responses)
            if (questionType == "TextQuestion"):
                chart = createTable(str(num), responses, question)
            return chart


# This class contains the details needed to be collected and attached to a given question within a survey.
class Question(Base):
    __tablename__ = 'QUESTION'
    id = Column(String(250), primary_key=True)
    type = Column(String(250))
    compulsory = Column(Boolean())
    question = Column(String(250))
    # NOTE: response will be empty if type is not equal to MCQ
    responses = Column(Json(500), default = [])
    deleted = Column(Json(500), default = False)

    # If type == TextQuestion this will be empty...
    def getResponses(self):
        return self.responses

    def getNumResponses(self):
        return len(self.responses)

    def __eq__(self, other):
        if(other == None):
            return False
        if(isinstance(other, Question)):
            return other.id == self.id
        return False

# This class is used to initialise/create textual response questions.
class TextQuestion(Question):
    def __init__(self, id, compulsory, question):
        if(len(question) < 1 or len(id) < 1):
            raise ValueError
            
        session = DBSession()
        self.id = id
        self.type = "TextQuestion"
        self.compulsory = compulsory
        self.question = question
        session.add(self)
        session.commit()

        
# This class is used to initialise/create multiple choice questions.
class MCQ(Question):
    def __init__(self, id, compulsory, question, responses):
        if(responses == None or len(responses) < 1 or len(question) < 1 or len(id) < 1):
            raise ValueError

        session = DBSession()
        self.id = id
        self.type = "MCQ"
        self.compulsory = compulsory
        self.question = question
        self.responses = responses
        session.add(self)
        session.commit()

