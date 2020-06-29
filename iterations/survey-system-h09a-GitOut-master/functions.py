"""
File: functions.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file contains helpler functions so that routes.py does
             does not become cluttered with indirect functions.
"""

# Imported libraries...
import random
import string
import server
import datetime
import time
from question import QuestionHandler, Question
from survey import Survey
from courses import SessionOffering
from users import User, Admin, Staff, Student, Guest, Unassigned
import copy
from authentication import forceLogin

# This function generates a random key for the survey URL using random letters and/or numbers.
def randomKey():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))

# This function is used to enrol a userID into a courseName, enabling them to access the survey in future.
def enrolUserToCourse(userId, courseName):
    # If the given course name is empty or not in the list of courses...
    if (courseName == "" or courseName == None):
        raise ValueError

    session = server.DBSession()
    user = session.query(User).filter(User.username == userId).first()
    # If the user is not in the list of users for the system...
    if (user == None):
        return -1
    # If the user is already registered in the course, an admin cannot add them to the same course for a second time...
    if (courseName in user.courses):
        return 0
    # If the information given passes the previous tests, then the user can be added to the course name given.
    userTemp = list(user.courses)
    userTemp.append(str(courseName))
    user.courses = userTemp

    session.add(user)
    session.commit()
    session.close()
    return 1

# This function is used to load all authenticated and unauthenicated guest users.
def loadAllGuestUsers():
    # Create new variables to allow for a new list of users to be added as valid users.
    session = server.DBSession()
    unassignedUsers = session.query(User).filter(User.role == "unassigned").all()
    guestUsers = session.query(User).filter(User.role == "guest").all()
    allGuestUsers = []

    # Append the unassigned users and guest users to the list of permitted users.
    for user in unassignedUsers:
        allGuestUsers.append(user)
    for user in guestUsers:
        allGuestUsers.append(user)
        
    return allGuestUsers

# This function switches a guest user between being approved or disabled from accessing the survey system.
def toggleAuthenticationUser(userId):
    session = server.DBSession()
    user = session.query(User).filter(User.username == userId).first()
    if (user.authenticated == False):
        user.authenticated = True
        user.role = "guest"
    else:
        user.authenticated = False
        user.role = "unassigned"
    session.add(user)
    session.commit()
    session.close()

# This function is used to remove a user id from the lsit of users registered in the session database.
def deleteUser(userId):
    session = server.DBSession()
    user = session.query(User).filter(User.username == userId).first()
    session.delete(user)
    session.commit()
    session.close()

# This function is used to load a survey from the session database.
def loadSurv(key):
    session = server.DBSession()
    survey = session.query(Survey).filter(Survey.key == key).first()
    currentTime = time.mktime(datetime.datetime.now().timetuple())
    if (survey != None and currentTime - survey.createtime > survey.activetime):
        survey.phase = 3
        survey.active = 0
    session.close()
    return survey

# This function will save a response submitted by a user into the survey system and append it the user's ID
# and their response to the database (linked to their course offering's survey being answered).
def saveResponse(survey, userId, responses):
    # If the survey is non-existent, return an error.
    if (survey == None):
        raise ValueError
    # If the user's survey response is empty, return an error.
    if (responses == None or len(responses) != len(survey.questions)):
        raise ValueError

    # Loop through the number of questions as this will indicate how long a user's response will be.
    for i, question in enumerate(survey.getQuestions()):
        if (responses[i] == '' and question.compulsory):
            raise ValueError

    session = server.DBSession()

    user = session.query(User).filter(User.username == userId).first()
    # If the user is not registered, return an error.
    if (user == None):
        return -1
    user = session.query(eval(user.role.title())).filter(User.username==userId).first()
    if (user == None):
        return -1

    # If the user is not registered, return an error.
    if (user == None):
        return -1

    userTemp = list(user.surveysResponded)
    userTemp.append(survey.key)
    user.surveysResponded = userTemp

    surveyTemp = list(survey.responses)
    surveyTemp.append(responses)
    survey.responses = surveyTemp

    session.add(user)
    session.add(survey)
    session.commit()
    session.close()

    forceLogin(userId)
    return 1

# This function loads all questions provided from the question pool.
def loadAllQuestions():
    session = server.DBSession()
    allQaa = []
    # Loop through all the questions that have not been deleted and append them to a list of 'all questions'.
    for question in session.query(Question).filter(Question.deleted == False).all():
        allQaa.append(question)
    session.close()
    return allQaa

# This function loads all optional questions provided from the question pool.
def loadOptionalQuestions():
    optionQaa = []
    session = server.DBSession()
    # Loop through all the optional questions that have not been deleted AND are not compulsory
    # and append them to a list of 'option questions'.
    for question in session.query(Question).filter(Question.deleted == False).filter(Question.compulsory == False).all():
        optionQaa.append(question)
        print(question.compulsory)
    session.close()
    return optionQaa

# This function searches for, loads and returns a question from the survey database, based on a key given.
def loadKeyedQuestion(key):
    session = server.DBSession()
    q = session.query(Question).filter(Question.id == key).first()
    session.close()
    return q

# This function is used to create an active survey given a key, name and description upon choosing survey creation.
def createSurv(key, active, phase, name, desc):
    session = server.DBSession()
    survey = Survey()
    survey.key = key
    survey.active = active
    survey.phase = phase
    currentTime = time.mktime(datetime.datetime.now().timetuple())
    survey.createtime = currentTime
    survey.name = name
    survey.desc = desc
    survey.questions = {}
    survey.responses = []
    session.add(survey)
    session.commit()
    session.close()
    return key

# This function is used to add a question to a given survey and can only be performed by an admin.
def addQuestion(surveyId, question, admin):
    # If the question is empty, return an error.
    if (question == None):
        raise ValueError

    session = server.DBSession()
    survey = session.query(Survey).filter(Survey.key == surveyId).first()

    # Add the given question into the dictionary of survey questions.
    temp = dict(survey.questions)
    temp[question] = admin
    survey.questions = temp

    session.add(survey)
    session.commit()
    session.close()

    return 1
  

# This function is used to delete a question from a given survey and given the survey's key.
def deleteQuestion(surveyId, key):
    session = server.DBSession()
    survey = session.query(Survey).filter(Survey.key == surveyId).first()
    survey.deleteQuestion(key)
    session.commit()
    session.close()

# This function is used to tie together a course and a survey and assigns the course survey a key so
# it can be accessed from the course class.
def associateCourse(course, key):
    session = server.DBSession()

    course.survey = key

    session.add(course)
    session.commit()
    session.close()

# This function loads in all session offerings from a file into course/session objects. It also
# associates any survey forms to that session offering if the association exists.
def loadAllCourseObjects():
    session = server.DBSession()
    courseObjects = []
    # Loop through the courses found in a session which are being offered and append them to a list of course objects.
    for course in session.query(SessionOffering).all():
        courseObjects.append(course)

    session.close()
    return courseObjects

# This function pushes the survey to the next phase.
def nextPhaseSurvey(survey):
    if (len(survey.questions) == 0):
        raise ValueError
        
    session = server.DBSession()
    survey.phase = survey.phase + 1

    if (survey.phase == 2):
        survey.active = 1

    if (survey.phase == 3):
        survey.active = 0

    session.add(survey)
    session.commit()
    session.close()

# This function is used to delete a survey given its linked course and the survey's key.
def deleteSurvey(course, key):
    session = server.DBSession()
    survey = session.query(Survey).filter(Survey.key == key).first()

    if (course != None):
        cour = session.query(SessionOffering).filter(SessionOffering.session == course.session).first()
        if (cour != None):
            cour.survey = None

    session.delete(survey)
    session.commit()
    session.close()
