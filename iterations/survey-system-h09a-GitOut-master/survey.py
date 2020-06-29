"""
File: survey.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file deals with the class of a survey and its functionalities.
"""

# Imported libraries...
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from server import Base
import server
from question import Question

from list import Json

# THis class contains the database table of a survey and the functions for obtaining and deleting question(s).
class Survey(Base):
    __tablename__ = 'SURVEY'
    key = Column(String(250), primary_key=True)
    active = Column(Boolean)
    phase = Column(Integer)
    createtime = Column(Integer)
    activetime = 3600
    name = Column(String(250))
    desc = Column(String(250))
    # json of question ids -> admin added
    questions = Column(Json(500))
    responses = Column(Json(500))

    # This function is used to obtain all the questions of a given survey and is returned in the form of a list.
    def getQuestions(self):
        allQaa = []
        session = server.DBSession()
        for id in self.questions.keys():
            q = session.query(Question).filter(Question.id == id).first()
            print(q.id)
            if(q != None):
                allQaa.append(q)

        session.close()
        return allQaa

    # This function will delete a given question from a survey.
    def deleteQuestion(self, question):
        temp = dict(self.questions)
        del temp[question.id]
        self.questions = temp
