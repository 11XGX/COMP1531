"""
File: routes.py
Date: 05 September 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This file is the 'controller'. It takes information given by the user
             at the presentation level; delegates work to the business functions/classes
             as needed, and; updates the model (database) / view (user HTML page) with
             the modified information.
"""

# Imported libraries...
from flask import Flask, flash, redirect, render_template, request, url_for
from server import app
from users import User, Admin, Staff, Student, Guest, Unassigned
from survey import Survey
from question import QuestionHandler, Question
from courses import SessionOffering
from statistics import createPieChart, createTable
import authentication
from functions import *
import os.path
import server

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("login"))

# This function is used to validate a user's login details, granting them their role's access to the survey system.
@app.route("/login", methods=["GET", "POST"])
def login():
    if (request.method == "POST"):
        if (request.form["bt"] == "login"):
            # Pass form information to the authentication module.
            success = authentication.login(request.form["username"], request.form["password"])
            if (success != 0 and success != -1):
                # Create a User() object based on the read-in role.
                server.user = success
                return redirect(url_for("landing"))
            elif (success == 0):
                flash("Account Still Pending Approval")
            else:
                flash("Incorrect Username or Password")
        if (request.form["bt"] == "requestaccess"):
            return redirect(url_for("requestAccess"))
    return render_template("login.html")

# This function deals with the landing page, from which other pages can be accessed from.
@app.route("/landing", methods=["GET", "POST"])
def landing():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    # The following are the Various page redirects which can occur based on the button pressed.
    if (request.method == "POST"):
        if (request.form["bt"] == "view_questions"):
            return redirect(url_for("viewQuestions"))
        if (request.form["bt"] == "create_questions"):
            return redirect(url_for("createQuestions"))
        if (request.form["bt"] == "view_surveys"):
            return redirect(url_for("viewSurveys"))
        if (request.form["bt"] == "create_surveys"):
            return redirect(url_for("createSurvey"))
        if (request.form["bt"] == "enrolment_manager"):
            return redirect(url_for("enrolmentManager"))
        if (request.form["bt"] == "logout"):
            authentication.logout()
            return redirect(url_for("login"))
        if (request.form["bt"] == "login"):
            return redirect(url_for("login"))
    return render_template("landing.html", is_authenticated = server.user.getPermissions(), user = server.user)

# This function writes new questions into the question pool.  The question pool is then saved to file/database.
numRes = 1
questionType = "TextQuestion"
@app.route("/createQuestions", methods=["GET", "POST"])
def createQuestions():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("landing"))
    # numRes stores the number of responses for this current question being created.
    global numRes, questionType
    # restore is a list that is used to carry information between page requests.
    restore = []
    # restoreOptional stores the checkmark for an optional box when a page is reloaded.
    restoreOptional = 0
    if request.method == "POST":
        # If the userhas requested a change in the questionType...
        if ("questionType" in request.form):
            questionType = request.form["questionType"]
            numRes = 1
        else:
            restoreList = MCQButtons(request, restore, restoreOptional, numRes)
            numRes = restoreList[0]
            restoreOptional = restoreList[1]
            if (request.form["bt"] == "back"):
                numRes = 1
                return redirect(url_for("landing"))
            # If the user requests to submit the questions, then append response list for each entry on form.
            if (request.form["bt"] == "submit_question"):
                submitNewQuestion(questionType, request)
                numRes = 1
    return render_template("questionForm.html", user = server.user, question = QuestionHandler, questionType = questionType, num = numRes, restore = restore, restoreOptional = restoreOptional, is_authenticated = server.user.getPermissions())

# This helper function manages the 'MCQ' control of a page.
def MCQButtons(request, restore, restoreOptional, numRes):
    # If the user requests to add a response, then reload this page with numRes += 1.
    if (request.form["bt"] == "add_response"):
        # The current input is also saved for when page is reloaded.
        restore.append(request.form["question"])
        for i in range(0, numRes):
            restore.append(request.form[str(i)])
        numRes += 1
        if ("optional" in request.form):
            restoreOptional = 1
    return [numRes, restoreOptional]

# This helper function is used in the createQuestions route.
def submitNewQuestion(questionType, request):
    if (request.form["question"] != ""):
        newQuestion = QuestionHandler.newQuestionRequest(randomKey(), questionType, request)
        if (newQuestion != 0):
            # Reset the number of responses on this page to 1.
            numRes = 1
            # Flash the user a message that this request was successful.
            flash("Your question was successfully added")
            # After a question is added, the user is redirected to the landing page.
            return redirect(url_for("landing"))
    flash("Invalid Question")

# This function is used for a page where the user can see all of the questions currently in the question pool.
@app.route("/viewQuestions", methods=["GET", "POST"])
def viewQuestions():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    questionPool = loadAllQuestions()
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (request.form["bt"][0] == "d"):
            deleteKey = request.form["bt"][1:]
            QuestionHandler.deleteQuestion(deleteKey)
            questionPool = loadAllQuestions()
    return render_template("viewQuestions.html", user = server.user, questions = questionPool, is_authenticated = server.user.getPermissions())


# This function is used for a page where the user can create a new survey.
# Upon creation, the user is redirected to the modify page to add questions from question pool.
@app.route("/createSurvey", methods=["GET", "POST"])
def createSurvey():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    # Create a list of sessionOffering objects for all sessions/courses.
    allSessions = loadAllCourseObjects()
    
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (request.form["name"].strip() != ""):
            # Create the new survey object from the HTML input fields.
            key = createSurv(randomKey(), 0, 0, request.form["name"].strip(), request.form["description"])
            # Append the new survey to its associated course.
            associateCourse(allSessions[int(request.form["course"])], key)
            # Redirect the user to the modify survey page after survey creation.
            return redirect(url_for("modifySurvey", key = key))
        else:
            # Flash the user a message for bad input.
            flash("Surveys must have a name and an associated course")
    return render_template("createSurvey.html", user = server.user, courses = allSessions, is_authenticated = server.user.getPermissions())

# This function is used to locate find surveys from the file/database and can have questions
# added to them from the question pool. Hence, all questions are required to be loaded.
numQues = 0
@app.route("/modifySurvey/<key>", methods=["GET", "POST"])
def modifySurvey(key):
    if (server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    # numQues stores the number of questions that are currently required for this survey.
    global numQues
    # restore is a list that allows user input to be saved across page requests.
    restore = []
    allQa = loadQuestionPoolForSurvey()
    # Load the survey with the given key from file. Returns 0 if unsuccessful.
    survey = loadSurv(key)
    currentQuestions = 0

    if (survey is not None):
        currentQuestions = survey.getQuestions()
        allQaa = [x for x in allQa if x not in survey.getQuestions()]

    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            numQues = 0
            return redirect(url_for("viewSurveys"))
        if (request.form["bt"][0] == "d"):
            numQues = deleteQuestionFromSurvey(numQues, key, request, restore, currentQuestions)
        if (request.form["bt"] == "create_questions"):
            return redirect(url_for("createQuestions"))
        # If the user requests to add another question to the survey, increase numRes and reload.
        if (request.form["bt"] == "add_question"):
            numQues = addQuestionToSurvey(numQues, request, restore)
        # If the user requests to submit this survey...
        if (request.form["bt"] == "submit_survey"):
            submitModifiedSurvey(numQues, key, request, restore)
            flash("Survey was successfully saved")
            # Reset the number of questions for this survey to 1 for subsequent surveys.
            numQues = 0
            return redirect(url_for("viewSurveys"))
    return render_template("modifySurvey.html", user = server.user, currentSurvey = survey, currentQuestions = currentQuestions, qp = allQaa, numQues = numQues, restore = restore, is_authenticated = server.user.getPermissions())

# This helper function is used for the modifySurvey route.
def loadQuestionPoolForSurvey():
    if (server.user.role == "admin"):
        # Read every question in pool from the csv into question objects (necessary for admin).
        allQaa = loadAllQuestions()
    else:
        allQaa = loadOptionalQuestions()
    return allQaa

# This helper function is used for the modifySurvey route.
def addQuestionToSurvey(numQues, request, restore):
    for i in range(0, numQues):
        # The current input is saved for page reload.
        restore.append(request.form[str(i)])
    numQues += 1
    return numQues

# This helper function is used for the modifySurvey route.
def deleteQuestionFromSurvey(numQues, survey, request, restore, currentQuestions):
    if (request.form["bt"][1] == "1"):
        deleteQuestion(survey, currentQuestions[int(request.form["bt"][2:])])
        del currentQuestions[int(request.form["bt"][2:])]
        for i in range(0, numQues):
            restore.append(request.form[str(i)])
    else:
        for i in range(0, numQues):
            if (int(request.form["bt"][2:]) != i):
                restore.append(request.form[str(i)])
        numQues -= 1
    return numQues

# This helper function is used for the modifySurvey route.
def submitModifiedSurvey(numQues, surveyId, request, restore):
    for i in range(0, numQues):
        # Load the question from the a key.
        newQuestion = loadKeyedQuestion(request.form[str(i)])
        addQuestion(surveyId, newQuestion.id, "undeletablequestions" in server.user.getPermissions()["modifysurvey"])



# This function is used for a page where the admin can view all current surveys,
# choose to modify them and change their 'active' status.
@app.route("/viewSurveys", methods=["GET", "POST"])
def viewSurveys(): 
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login")) 
    allSessions = server.user.getCourses()
    responseRegistered = server.user.hasRespondedSurveys(allSessions)
    if (server.user.role == "admin"):
        allSessions = loadAllCourseObjects()
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        # Recall data from the value of the button pressed.
        request_data = request.form["bt"].split(" ")
        survey = allSessions[int(request_data[1])].getSurvey()
        # If the button value [0] was 'm' it was a request to modify the survey...
        if (request_data[0] == 'm'):
            return redirect(url_for("modifySurvey", key = survey.key))
        # If the button value [0] was 'p' it was a request to phase the survey...
        if (request_data[0] == 'p'):
            nextPhaseSurvey(survey)
        # If the button value [0] was 'd' it was a request to delete the survey...
        if (request_data[0] == 'd'):
            deleteSurvey(allSessions[int(request_data[1])], survey.key)
    return render_template("viewSurveys.html", user = server.user, sessions = allSessions, responseRegistered = responseRegistered, is_authenticated = server.user.getPermissions())

# This function uses a keyed link which is required for public access. An admin can view the published survey here.
# Public respondents can complete the surveys here also.
@app.route("/survey/<key>", methods=["GET", "POST"])
def survey(key):
    if (server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    # Load the survey with the given key from file. Returns 0 if unsuccessful.
    survey = loadSurv(key)
    surveyQuestions = 0
    if (survey is not None):
        # Load question objects for questions that are only found in the survey.
        surveyQuestions = survey.getQuestions()
    # Check if this user already has response registered...
    responseRegistered = server.user.hasRespondedSurvey(key)
    # Check if the user is already enrolled in the course associated to the survey...
    participate = server.user.userCanParticiplate(key)
    if (request.method == "POST"):
        # Check that all compulsory questions have a valid response...
        if validateCompulsory(surveyQuestions, request) == 0:
            flash("Compulsory Questions Must Have Responses")
        else:
            submitSurveyForm(survey, surveyQuestions, request)
            return redirect(url_for("viewSurveys"))
    return render_template("surveyForm.html", currentSurvey = survey, questions = surveyQuestions, responseRegistered = responseRegistered, participate = participate, is_authenticated = server.user.getPermissions())

# This helper function is used for the surveys route. It checks to make sure that all
# questions marked as compulsory have some response.
def validateCompulsory(surveyQuestions, request):
    for i in range(0, len(surveyQuestions)):
        if (int(surveyQuestions[i].compulsory) == 1):
            if (str(i)) in request.form and request.form[str(i)].strip() == "":
                return 0
            elif (str(i)) not in request.form:
                return 0
    return 1

# This helper function is used for the surveys route. It saves the responses of the
# survey into the specific survey's own response file and registers submission by
# the user in respondents file.
def submitSurveyForm(survey, surveyQuestions, request):
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    responses = []
    for i in range(0, len(surveyQuestions)):
        if (str(i) in request.form):
            # Only store solutions.
            responses.append(request.form[str(i)])
        else:
            responses.append("")
    saveResponse(survey, server.user.username, responses)

# THis function is used for the route that shows the results of a survey, including visualisations.
@app.route("/surveyResult/<key>", methods=["GET", "POST"])
def surveyResult(key):
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    survey = loadSurv(key)
    surveyQuestions = 0
    surveyHasResponses = 0
    if (survey is not None):
        surveyQuestions = survey.getQuestions()
        surveyHasResponses = len(survey.responses) > 0
    else:
        survey = 0
    # Check if the user is currently enrolled in the course associated to the survey...
    participate = server.user.userCanParticiplate(key)
    charts = []
    print(surveyQuestions)
    # For each question in the survey, create a chart, only if the survey form exists.
    if (surveyQuestions != 0 and surveyHasResponses):
        for i in range(0, len(surveyQuestions)):
            temp = []
            for row in survey.responses:
                temp.append(row[i])

            chart = QuestionHandler.getChart(surveyQuestions[i].type, i, surveyQuestions[i].question, temp)
            charts.append(chart)
    return render_template("surveyResult.html", survey = survey, questions = surveyQuestions, hasResponses = surveyHasResponses, participate = participate, charts = charts, is_authenticated = server.user.getPermissions())

# This function is used to manage the enrolment of students within the survey system.
@app.route("/enrolmentManager", methods=["GET", "POST"])
def enrolmentManager():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (request.form["bt"] == "enroltocourse"):
            return redirect(url_for("enrolToCourse"))
        if (request.form["bt"] == "manageguests"):
            return redirect(url_for("guestManager"))
    return render_template("enrolmentManager.html", user = server.user)

# This function is used to enrol/assign a studet to a course.
@app.route("/enrolToCourse", methods=["GET", "POST"])
def enrolToCourse():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    # Createa a list of session offering objects for all sessions/courses.
    allSessions = loadAllCourseObjects()
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("enrolmentManager"))
        enrolRequest = enrolUserToCourse(request.form["username"].strip(), allSessions[int(request.form["course"])].session)
        if (enrolRequest == 1):
            flash("User "+str(request.form["username"].strip())+" was enrolled to "+str(allSessions[int(request.form["course"])].session))
        elif (enrolRequest == 0):
            flash("User already enrolled in this course")
        else:
            flash("User Not Found")
    return render_template("enrolToCourse.html", user = server.user, courses = allSessions)

# This function manages users registered as a guest within the survey system.
@app.route("/guestManager", methods=["GET", "POST"])
def guestManager():
    if(server.user.role == 'unassigned'):
        return redirect(url_for("login"))
    guestUsers = loadAllGuestUsers() 
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("enrolmentManager"))
        requestString = request.form["bt"]
        if (requestString[0] == "a"):        # Authenticated flag toggle
            toggleAuthenticationUser(requestString[2:])
        if (request.form["bt"][0] == "d"):   # Delete the user
            deleteUser(requestString[2:])
        return redirect(url_for("guestManager"))
    return render_template("guestManager.html", user = server.user, guestUsers = guestUsers)


# This function is used in the route in which guests can submit a username,
# password, course of interest to become a guest member of the survey system.
@app.route("/requestAccess", methods=["GET", "POST"])
def requestAccess():
    allSessions = loadAllCourseObjects()
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("login"))
        guestRequest = authentication.createGuestRequest(request.form["username"].strip(), request.form["password"], allSessions[int(request.form["course"])].session)
        if (guestRequest == -1):
            flash("Username already exists")
        else:
            flash("Request submitted. Review in process.")
    return render_template("requestAccess.html", user = server.user, courses = allSessions)

