from flask import Flask, flash, redirect, render_template, request, url_for
from server import app
from users import User, Admin, Staff, Student
from survey import Survey
from question import QuestionHandler, Question, TextQuestion, MCQ
from fileReader import CSVReader
from fileWriter import CSVWriter
from courses import SessionOffering
from statistics import createPieChart
import authentication
from functions import *
import os.path
import server

# Routes is the 'controller'. It should: 
# Take information given by the user at the presentation level,
# delegate work to the business functions/classes as needed, 
# update the model (database) / view (user html page) with the modified information.

# CHANGELIST from iteration 1
# Localised questiontype code into obvious, minimal areas that can be easily extended onto.
#   Extending on a new questionType in the future will involve:
#       - Creating a new subclass that inherits from the abstract Question() class. Mandatory functions enforced by @abstractmethod
#       - Respectively modifying questionForm.html and surveyForm.html to add the html templating of how these new question types are created and how they are responded to
#   Question class also had some 'helper' functions pulled out of it and these are now grouped together in a QuestionHandler static class
#
# Each session offering now only supports one survey at a time (as per the specifications).
# 
# When a surveyForm is loaded - the questions are not loaded from the questionPool but rather loaded directly from the surveyForm itself. Hence the surveyForm
# has to store its own questions. Cannot rely on the questionPool as older questions may be deleted from the pool. In such a case, the specifications say that
# questions deleted from the question pool should persist in the surveyForm.
#   In Implementing the above, some other changes were made:
#       - There is no longer a surveys.csv that stores a survey per row
#       - Rather each survey has its own surveyform_[key].csv created. Equivalent to each survey having its own database table. Required for questions to persist.
#   As of right now, creating a survey for a session that already has one will: overwrite the association between the session and its older survey. The older survey will still 
#   persist. 
#
# Ability to delete questions from the questionPool. Also involved making the viewQuestions.html page. Very basic page at the moment. Could have features added if wanted.
#
# When modifying a survey - the questions that are CURRENTLY in the survey can be deleted but cannot be changed via a dropdown box. The reason for this change (previously
# older questions could be changed using a dropdown box) is that questions currently in the survey form may be deleted.
# This still suffices for the survey workflow criteria, since older questions still may be deleted if a staff member reviewing the survey wishes so. Questions
# can be easily added as per before.
#
# Survey workflow was added. This means when an admin creates a server - the survey phase is set to 0. When the admin is happy with the survey, they may push it
# to phase 1. In phase 1, staff members associated with that course are able to see the survey. They can edit the survey in the following ways:
#   - Adding and deleting questions that are flagged 'optional'. Admin questions cannot be deleted however.
# When the staff is happy with the survey, or if the admin wishes, the survey can then be pushed to phase 2 by either an admin or associated staff. 
# In phase 2, the survey will now appear on the dashboard of students who are now able to click the survey link. They can then fill out the survey.
# Note that staff members cannot enter a survey response but admins can.
#
# User class was added. Built with OCP in mind.
# The users class will have one user instantiated which can be accessed at server.user
# At login, this user will have all of their courses associated with them as well as the courses being loaded into course objects. 
# For each course, if their exists a survey, the survey will also be loaded into a survey object. 
# The associated course objects and survey objects for the user can then be easily accessed via the user class which link to these objects.
# Another important feature of users, is there permissions dictionary. This dictionary stores a things that the user can do.
# This makes extension easier in the case that new users types are required in the future. Rather than going through each old HTML page and adding a {% if user == ... %}
# only the permission needs to be added to the user's permission dictionary and this is compared in the HTML pages throguh jinja and hence each HTML page will not need to be changed.
#
# Added new .csv file called "respondents.csv". This 'table' has two columns. The first column is a userID and the second column is a survey key.
# When a user submits a survey, a new entry to this table is added (new row). This shows that a user has submitted a reponse for a particular survey. However, it is
# stored completely indepent from the reponseform and hence anonomous. 
#
# A 'student' may view and complete 'active' surveyforms that are in 'phase 2' for the courses in which they are enrolled. Viewing of the actual form is only allowed if the user 
# has not already responded and is not an admin. Hence only one response is permitted for students.
# 'Staff' users do not have permission to access any survey forms. 
# 'Admin' users may complete survey forms. They may do this an unlimited number of times. 
#
# Staff members can no longer alter/delete questions added by an admin. On top of this, staff members may only add questions from the optional questionpool. 
# Staff members can remove questions that they themself have added or other staff members have added.
#
# Surveys can only be created for a course if that course does not already have a survey associated with it. This is enforced by excluding courses for selection from
# the dropdown box in createSurvey.html if that session object already has a survey associated with it.
# 
# Compulsory questions are now enforced during the filling out of the survey form. These questions are marked with a * and an error user message is flashed if all
# compulsory questions are not filled out.
#
# Added metrics to surveys. !!! Uses a library that you need to install in your virtualenv for it to work (import plotly) !!!
# These metrics are viewable to an admin at any time. For staff members and students are only avaialable in the "closed" phase.

# TODO Change from a CSV system to a database system. Involves making databases that are similar in structure to how the current csv files are being used. Also
# involves making functions to replace the current functions that are reliant on CSV format.

# TODO "Metrics Page" - Dedicated page just for results? Results already linked on viewsurvey page.

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method == "POST"):                                       
        success = authentication.login(server.usersCSVReader, request.form["username"], request.form["password"])       # Pass form information to authentication module
        if (success):                                
            userString = authentication.user_role.title()+"("+request.form["username"]+")"
            server.user = eval(userString)                                                                              # Create a User() object based on read-in role          
            coursesToUser(server.enrolmentsCSVReader, server.coursesCSVReader, server.user)                             # Load the course objects and survey forms associated to user
            return redirect(url_for("landing"))
        else:
            flash("Incorrect Username or Password")
    return render_template("login.html")


# The landing page, where other pages can be accessed from
@app.route("/landing", methods=["GET", "POST"])
def landing():
    # Various page redirects based on the button pressed
    if (request.method == "POST"):
        if (request.form["bt"] == "view_questions"):
            return redirect(url_for("viewQuestions"))
        if (request.form["bt"] == "create_questions"):
            return redirect(url_for("createQuestions"))
        if (request.form["bt"] == "view_surveys"):
            return redirect(url_for("viewSurveys"))
        if (request.form["bt"] == "create_surveys"):
            return redirect(url_for("createSurvey"))
        if (request.form["bt"] == "logout"):
            authentication.logout()
            return redirect(url_for("login"))
        if (request.form["bt"] == "login"):
            return redirect(url_for("login"))
    return render_template("landing.html", is_authenticated = server.user.getPermissions())


# Write new questions into the question pool. Question pool saved to file/database
numRes = 1
questionType = "TextQuestion"
@app.route("/createQuestions", methods=["GET", "POST"]) 
def createQuestions():
    global numRes, questionType, Question                                                       # numRes stores the number of reponses for this current question being created
    restore = []                                                                                # restore is a list that is used to carry information between page requests
    restoreOptional = 0                                                                         # restores the checkmark for optional box when page reloaded
    if request.method == "POST":   
        if ("questionType" in request.form):                                                    # user changed the questionType  
            questionType = request.form["questionType"]     
            numRes = 1                                                               
        else:
            restoreList = MCQButtons(request, restore, restoreOptional, numRes)
            numRes = restoreList[0]
            restoreOptional = restoreList[1]
            if (request.form["bt"] == "back"):                                  
                numRes = 1
                return redirect(url_for("landing"))
            if (request.form["bt"] == "submit_question"):                           # If the user requests to submit the questions, then append response list for each entry on form
                submitNewQuestion(questionType, request)
                numRes = 1
    return render_template("questionForm.html", question = QuestionHandler, questionType = questionType, num = numRes, restore = restore, restoreOptional = restoreOptional, is_authenticated = server.user.getPermissions())    

# Subfunction that manages the 'MCQ' Control of page
def MCQButtons(request, restore, restoreOptional, numRes):
    if (request.form["bt"] == "add_response"):                                                      # If the user requests to add a response, then reload this page with numRes += 1
        restore.append(request.form["question"])                                                    # Current input is also saved for when page is reloaded 
        for i in range(0, numRes):
            restore.append(request.form[str(i)])                                                
        numRes += 1 
        if ("optional" in request.form):
            restoreOptional = 1
    return [numRes, restoreOptional]

# Helper function for createQuestions route
def submitNewQuestion(questionType, request):
    if (request.form["question"] != ""):
        newQuestion = QuestionHandler.newQuestionRequest(randomKey(), questionType, request)
        saveNewQuestion(server.qaaCSVWriter, newQuestion)                                           # Tell the qaaCSV object to write this new question into the relevent csv file
        numRes = 1                                                                                  # Reset the number of responses on this page to 1
        flash("Your question was successfully added")                                               # Flash the user a message that this request was successful
        return redirect(url_for("landing"))                                                         # After the question is added - the user is redirected to the landing page
    else: 
        flash("Question box must have text")


# A page where the user can see all of the questions currently in the question pool
@app.route("/viewQuestions", methods=["GET", "POST"])
def viewQuestions():
    questionPool = loadAllQuestions(server.qaaCSVReader)
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (request.form["bt"][0] == "d"):
            deleteKey = request.form["bt"][1:]
            deleteQuestion(server.qaaCSVWriter, server.qaaCSVReader, deleteKey)
            questionPool = loadAllQuestions(server.qaaCSVReader)
    return render_template("viewQuestions.html", questions = questionPool, is_authenticated = server.user.getPermissions())


# A page where the user can create a new survey
# Upon creation, redirected to modify page to add questions from question pool
@app.route("/createSurvey", methods=["GET", "POST"])
def createSurvey():
    allSessions = loadAllCourseObjects(server.coursesCSVReader)                             # Creates a list of sessionOffering objects for all sessions/courses
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (request.form["name"].strip() != ""):
            newSurvey = Survey(randomKey(), 0, 0, request.form["name"].strip(), request.form["description"], [0])                   # Make the new survey object from HTML input fields
            writeSurvey(CSVWriter("csv/surveyform_"+newSurvey.getKey()+".csv"), server.qaaCSVReader, newSurvey, [])                 # Write a new survey form csv
            compoundKey = [allSessions[int(request.form["course"])].getName(), allSessions[int(request.form["course"])].getSession()] # Create the compound key required for search
            associateCourse(server.coursesCSVReader, server.coursesCSVWriter, compoundKey, newSurvey.getKey())                      # Append the new survey onto its associated course
            return redirect(url_for("modifySurvey", key = newSurvey.getKey()))                                                      # Redirect to modify survey page after creation
        else:
            flash("Surveys must have a name and an associated course")                                                              # Flash user message for bad input
    return render_template("createSurvey.html", courses = allSessions, is_authenticated = server.user.getPermissions())


# Surveys found in file/database can have questions added to them from question pool. Hence all questions required to be loaded.
numQues = 0
@app.route("/modifySurvey/<key>", methods=["GET", "POST"])
def modifySurvey(key):
    global numQues                                                                          # numQues stores the number of questions that are currently required for this survey
    restore = []                                                                            # restore is a list that allows user input to be saved across page requests        
    survey = loadSurvey(key)                                                                # Load the survey with the given key from file. Returns 0 if unsuccessful
    currentQuestions = loadSurveyQuestions(key)	 
    allQaa = loadQuestionPoolForSurvey()
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            numQues = 0
            return redirect(url_for("viewSurveys"))
        if (request.form["bt"][0] == "d"):
            numQues = deleteQuestionFromSurvey(numQues, survey, request, restore, currentQuestions)
        if (request.form["bt"] == "create_questions"):
            return redirect(url_for("createQuestions"))                                       
        if (request.form["bt"] == "add_question"):                                          # If the user requests to add another question to the survey, increase numRes and reload
            numQues = addQuestionToSurvey(numQues, request, restore)
        if (request.form["bt"] == "submit_survey"):                                         # If the user requests to submit this survey
            submitModifiedSurvey(numQues, survey, request, restore)
            flash("Survey was successfully saved")
            numQues = 0                                                                      # Reset the number of questions for this survey to 1 for subsequent surveys
            return redirect(url_for("viewSurveys"))
    return render_template("modifySurvey.html", currentSurvey = survey, currentQuestions = currentQuestions, qp = allQaa, numQues = numQues, restore = restore, is_authenticated = server.user.getPermissions())

# Helper function for modifySurvey route
def loadQuestionPoolForSurvey():
    if (server.user.getRole() == "admin"): 
        allQaa = loadAllQuestions(server.qaaCSVReader)                                      # Read every question in pool from the csv into question objects. Neccessary for admin.
    else:
        allQaa = loadOptionalQuestions(server.qaaCSVReader) 
    return allQaa 

# Helper function for modifySurvey route
def addQuestionToSurvey(numQues, request, restore):
    for i in range(0, numQues):                                                             
        restore.append(request.form[str(i)])                                                # Also current input saved for page reload
    numQues += 1    
    return numQues

# Helper function for modifySurvey route
def deleteQuestionFromSurvey(numQues, survey, request, restore, currentQuestions): 
    if (request.form["bt"][1] == "1"):
        del currentQuestions[int(request.form["bt"][2:])]
        writeSurvey(CSVWriter("csv/surveyform_"+survey.getKey()+".csv"), server.qaaCSVReader, survey, currentQuestions) # Overwrite the survey form
        for i in range(0, numQues):                                                         
            restore.append(request.form[str(i)])               
    else:
        for i in range(0, numQues):   
            if (int(request.form["bt"][2:]) != i):                                                      
                restore.append(request.form[str(i)])                                      
        numQues -= 1
    return numQues

# Helper function for modifySurvey route
def submitModifiedSurvey(numQues, survey, request, restore):
    questions = loadSurveyQuestions(survey.getKey())                                        # Append the older, previous questions back to the survey
    for i in range(0, numQues):
        newQuestion = loadKeyedQuestion(server.qaaCSVReader, request.form[str(i)])          # Load the question from the key 
        if ("undeletablequestions" in server.user.getPermissions()["modifysurvey"]):        # Anyone with this permission can create questions that only this permission can delete
            newQuestion.setAdminAdded(1)
        questions.append(newQuestion)                                           
    writeSurvey(CSVWriter("csv/surveyform_"+survey.getKey()+".csv"), server.qaaCSVReader, survey, questions)            # Overwrite the survey form


# A page where the admin can view all current surveys, choose to modify them, change their 'active' status etc.
@app.route("/viewSurveys", methods=["GET", "POST"])
def viewSurveys(): 
    allSessions = server.user.getCourses()
    responseRegistered = userHasRespondedSurveys(server.respondentsCSVReader, server.user.getUsername(), allSessions)
    if (server.user.getRole() == "admin"):
        allSessions = loadAllCourseObjects(server.coursesCSVReader)  
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        request_data = request.form["bt"].split(" ")                                        # Bring back data from the value of the button pressed
        survey = allSessions[int(request_data[1])].getSurvey()
        if (request_data[0] == 'm'):                                                        # If the button value [0] was 'm' it was a request to modify the survey
            return redirect(url_for("modifySurvey", key = survey.getKey()))
        if (request_data[0] == 'a'):                                                        # Else it was a request to change the 'active' status of the survey
            activateToggleSurvey(survey)
        if (request_data[0] == 'p'):
            nextPhaseSurvey(survey)
        if (request_data[0] == 'd'):                                                                 
            deleteSurvey(server.coursesCSVReader, server.coursesCSVWriter, allSessions[int(request_data[1])], survey.getKey())
    return render_template("viewSurveys.html", sessions = allSessions, responseRegistered = responseRegistered, is_authenticated = server.user.getPermissions())


# Keyed link is required for public access. Admin can view the published survey here. Public respondents can complete the surveys here too.
@app.route("/survey/<key>", methods=["GET", "POST"])
def survey(key):                                                                                  
    survey = loadSurvey(key)                                                                # Load the survey with the given key from file. Returns 0 if unsuccessful
    surveyQuestions = loadSurveyQuestions(key)                                              # Load question objects for only questions that are found in the survey 
    responseRegistered = userHasRespondedSurvey(server.respondentsCSVReader, server.user.getUsername(), key) # Check if this user already has response registered
    participate = userCanParticiplate(server.user, key)                                     # Check if the user is enrolled in the course associated to the survey
    if (request.method == "POST"):              
        if validateCompulsory(surveyQuestions, request) == 0:                               # Check that all compulsory questions have a valid response
            flash("Compulsory Questions Must Have Responses")   
        else :                                           
            submitSurveyForm(survey, surveyQuestions, request)
            return redirect(url_for("viewSurveys"))
    return render_template("surveyForm.html", currentSurvey = survey, questions = surveyQuestions, responseRegistered = responseRegistered, participate = participate, is_authenticated = server.user.getPermissions())

# Helper function for surveys route. Checks to make sure that all questions marked compulsory have some response
def validateCompulsory(surveyQuestions, request):
    for i in range(0, len(surveyQuestions)):
        if (int(surveyQuestions[i].getCompulsory()) == 1): 
            if (str(i)) in request.form and request.form[str(i)].strip() == "":
                return 0
            elif (str(i)) not in request.form:
                return 0  
    return 1

# Helper function for surveys route. Saves the responses of the survey into the specific surveys own response file and registeres submission by the user in respondents file
def submitSurveyForm(survey, surveyQuestions, request):
    responses = []
    for i in range(0, len(surveyQuestions)):
        if (str(i) in request.form):
            responses.append(request.form[str(i)])                                      # Only store solutions
        else:
            responses.append("")
    surveyFormWriter = CSVWriter("csv/surveyresponse_"+survey.getKey()+".csv")          # Only the writer is required here
    surveyFormWriter.append(responses)                                                  # Also write the responses into the csv file
    server.respondentsCSVWriter.append([server.user.getUsername(), survey.getKey()])    # Mark in an indepdent file that the user has completed this survey 


# The route that shows the results of a survey including visualisations 
@app.route("/surveyResult/<key>", methods=["GET", "POST"])
def surveyResult(key):
    survey = loadSurvey(key)  
    surveyQuestions = loadSurveyQuestions(key) 
    participate = userCanParticiplate(server.user, key)                                 # Check if the user is enrolled in the course associated to the survey 
    surveyHasResponses = hasResponses(key)                                              
    charts = []
    if (surveyQuestions != 0 and surveyHasResponses):                                   # For each question in the survey, create a chart. Only if the survey form exists.       
        for i in range(0, len(surveyQuestions)):
            questionResponses = CSVReader("csv/surveyresponse_"+str(key)+".csv").readColumn(i)
            chart = createPieChart(str(i), questionResponses)
            charts.append(chart)
   
    return render_template("surveyResult.html", survey = survey, questions = surveyQuestions, hasResponses = surveyHasResponses, participate = participate, charts = charts, is_authenticated = server.user.getPermissions())

