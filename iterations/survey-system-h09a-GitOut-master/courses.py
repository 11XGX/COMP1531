"""
File: courses.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file contains the class for a course session offering and the
             function for obtaining a survey using a provided key.
"""

# Imported libraries...
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from server import Base
import server
from survey import Survey
import datetime
import time

# This class handles the reading of courses into the form of a database table.
class SessionOffering(Base):
    __tablename__ = 'SESSIONOFFERING'
    session = Column(String(250), primary_key=True)
    # Survey key:
    survey = Column(String(250))

    # This function opens a database session in order to search for a given survey from the query of a user.
    def getSurvey(self):
        session = server.DBSession()
        surv = session.query(Survey).filter(Survey.key == self.survey).first()
        currentTime = time.mktime(datetime.datetime.now().timetuple())
        if (surv != None and currentTime - surv.createtime > surv.activetime):
            surv.phase = 3
            surv.active = 0
        session.close()
        return surv

