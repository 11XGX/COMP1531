from flask import Flask, flash, redirect, render_template, request, url_for
from server import app, user_authenticated
from surveyClass import Survey
from questionClass import Question
import hashlib
from functions import *
import os.path
import csv
import server


@app.route("/", methods=["GET", "POST"])
def index():
#default entry page
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method == "POST"):                                                               # Since this page has one button (login), a "POST" request means the user clicked login
        # load user details from users.csv
        users = server.usersCSV.readPairs()                                                     

        # check if form details match an entry in users
        name = request.form["name"]
        password = hashlib.pbkdf2_hmac('sha256', request.form["password"].encode('utf-8'), b'salt', 150000)
        if (name in users and password.hex() == users[name]):                                   # Check if the given user name and corresponding password are a match
            server.user_authenticated = True                                                           # 'Logs' the user in
            return redirect(url_for("landing"))
        else:
            flash("Incorrect username or password")                                             # If an incorrect combination is given - flash the user a message
    return render_template("login.html")


# The 'admin' landing page, where other pages can be accessed from
@app.route("/landing", methods=["GET", "POST"])
def landing():
    # Various page redirects based on the button pressed
    if (request.method == "POST"):
        if (request.form["bt"] == "view_questions"):
            pass
        if (request.form["bt"] == "create_questions"):
            return redirect(url_for("createQuestions"))
        if (request.form["bt"] == "view_surveys"):
            return redirect(url_for("viewSurveys"))
        if (request.form["bt"] == "create_surveys"):
            return redirect(url_for("createSurvey"))
        if (request.form["bt"] == "login"):
            return redirect(url_for("login"))
    return render_template("landing.html", is_authenticated = server.user_authenticated)


# Write new questions into the question pool. Question pool saved to file/database
numRes = 1
@app.route("/createQuestions", methods=["GET", "POST"]) 
def createQuestions():
    global numRes                                                                               # numRes stores the number of reponses for this current question being created
    restore = []                                                                                # restore is a list that is used to carry information between page reloads so that a user does not have to retype entries into the input fields after requesting a new response box etc.
    if request.method == "POST":                                                                    
        if (request.form["bt"] == "back"):                                  
            numRes = 1
            return redirect(url_for("landing"))
        if (request.form["bt"] == "add_response"):                                              # If the user requests to add a response, then reload this page with numRes += 1
            restore.append(request.form["question"])                                            # Current input is also saved for when page is reloaded 
            for i in range(0, numRes):
                restore.append(request.form[str(i)])                                                
            numRes += 1
        if (request.form["bt"] == "submit_question"):                                           # If the user requests to submit the questions, then append responses list with the entry in the request form. Do this for the number of responses that this question has.
            if (request.form["question"] != ""):
                responses = []
                for i in range(0, numRes):
                    if (request.form[str(i)] != ""):
                        responses.append(request.form[str(i)])
                newQuestion = Question(1, request.form["question"], responses)                  # Create a new question object and construct with given input
                server.qaaCSV.append(newQuestion.getCSVRow())                                   # Tell the qaaCSV object to write this new question into the relevent csv file
                numRes = 1                                                                      # Reset the number of responses on this page to 1
                flash("Your question was successfully added")                                   # Flash the user a message that this request was successful
                return redirect(url_for("landing"))                                             # After the question is added - the user is redirected to the landing page
            else: 
                flash("Question box must have text")
    return render_template("createQuestions.html", num = numRes, restore = restore, is_authenticated = server.user_authenticated)    


# A page where the user can create a new survey
# Upon creation, redirected to modify page to add questions from question pool
@app.route("/createSurvey", methods=["GET", "POST"])
def createSurvey():
    courseList = server.coursesCSV.readRow()                                                    # Read the given courses.csv file to determine currently available courses
    courseList = courseList[1:]                                                                 # Get rid of the first entry in the courseList (which is some generic text)
    for i in range(0, len(courseList)): # change from len(courseList) - 1 to just len(courseList) since the range function does not include the higher range
        courseList[i] = str(courseList[i]).replace("[", "").replace("]", "").replace("'", "")   # Get rid of certain characters from the course list elements

    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (request.form["name"].strip() != ""):
            newSurvey = Survey(randomKey(), 0, request.form["course"], request.form["name"].strip(), request.form["description"], [0])      # Create a new survey object and intialise it with values based on the values of certain form members in the HTML page
            server.surveyCSV.append(newSurvey.getCSVRow())                                          # Write this survey to the csv file
            return redirect(url_for("modifySurvey", written_row = server.surveyCSV.numRow() - 1))   # After a new survey is created, user immediately redirect to modify page
        else:
            flash("Surveys must have a name and an associated course")                              # Flash user message if the page inputs are bad when creating a survey
    return render_template("createSurvey.html", courses = courseList, is_authenticated = server.user_authenticated)


# Surveys found in file/database can have questions added to them from question pool. Hence all questions required to be loaded.
# Should take argument of which survey to modify (given by row in CSV file). Later questions should have unique keys, so that if CSV rows changed - still readable
numQues = 1
@app.route("/modifySurvey/<written_row>", methods=["GET", "POST"])
def modifySurvey(written_row):
    global numQues                                                                          # numQues stores the number of questions that are currently required for this survey
    restore = []                                                                            # restore is a list that allows user input to be transferred/saved across page requests

    if (int(written_row) >= server.surveyCSV.numRow() or int(written_row) < 0):             # If index requested (<written_row>) will be out of range, change it
        return redirect(url_for("modifySurvey", written_row = server.surveyCSV.numRow() - 1))

    row = server.surveyCSV.readOneRow(int(written_row))                                     # Read the currently-being-modified survey into a survey object
    s = Survey(row[0], row[1], row[2], row[3], row[4], row[5])                              # Note that questions are reset when a survey is modified          
    allQaa = []                                                                             # Read every question in pool from the csv into question objects. Neccessary as this survey may include any of these questions at the users choice
    for row in server.qaaCSV.readAllRows():
        q = Question(1, row[0], row[1:])
        allQaa.append(q)                                                                          
    
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            numQues = 1
            return redirect(url_for("viewSurveys"))
        if (request.form["bt"] == "add_question"):                                          # If the user requests to add another question to the survey, increase numRes and reload
            for i in range(0, numQues):                                                             
                restore.append(int(request.form[str(i)]))                                   # Also current input saved for page reload
            numQues += 1
        if (request.form["bt"] == "submit_survey"):                                         # If the user requests to submit this survey
            s.clearQuestions()                                                              # Clear any current questions that the survey may have had
            for i in range(0, numQues):                                                     # Append the questions from the HTML form inputs onto this survey object
                s.addQuestion(request.form[str(i)])                                                
                restore.append(int(request.form[str(i)])) 
            server.surveyCSV.replaceRow(int(written_row), s.getCSVRow())                    # Replace the row that contained the old version of this survey with the new survey
            flash("Survey was successfully saved")
            numQues = 1                                                                     # Reset the number of questions for this survey to 1 for subsequent surveys
            return redirect(url_for("viewSurveys"))
    else:
        restore = list(s.getQuestions())  
        numQues = len(restore)

    return render_template("modifySurvey.html", currentSurvey = s, qp = allQaa, numQues = numQues, written_row = written_row, restore = restore, is_authenticated = server.user_authenticated)


# A page where the admin can view all current surveys, choose to modify them, change their 'active' status etc.
@app.route("/viewSurveys", methods=["GET", "POST"])
def viewSurveys():
    allSurvey = []                                                                          # Load all surveys found in the relevent csv file into survey objects
    for row in server.surveyCSV.readAllRows():
        s = Survey(row[0], row[1], row[2], row[3], row[4], row[5])
        allSurvey.append(s)
    # Responses not required for this iteration. Not loaded.
    
    if (request.method == "POST"):
        if (request.form["bt"] == "back"):
            return redirect(url_for("landing"))
        if (int(request.form["bt"]) % 2 == 0):                                                          # If the button value is % 2 then it was a request to modify the survey
            return redirect(url_for("modifySurvey", written_row = int(int(request.form["bt"])/2)))
        if (int(request.form["bt"]) % 2 != 0):                                                          # Else it was a request to change the 'active' status of the survey
            allSurvey[int((int(request.form["bt"]) - 1) / 2)].alternateActive()                                                                         # Change active status
            server.surveyCSV.replaceRow(int((int(request.form["bt"]) - 1) / 2), allSurvey[int((int(request.form["bt"]) - 1) / 2)].getCSVRow())          # Save this change to csv

    return render_template("viewSurveys.html", allSurvey = allSurvey, is_authenticated = server.user_authenticated)


# Keyed link is required for public access. Admin can view the published survey here. Public respondents can complete the surveys here too.
@app.route("/survey/<key>", methods=["GET", "POST"])
def survey(key):
    valid = True                                                                                    # 'valid' boolean is used to check whether <key> in the web address is valid
    s = []                                                                                          # 's' will contain the information about the survey to be completed
    row = server.surveyCSV.readKeyedRow(key)                                                        # Read in from csv the row that contains the given <key>
    if row == []:                                                                                   # If row is empty then no csv row had the given <key>. Hence invalid key
        valid = False
    if valid:                                                                                       # If the key was valid then create the appropriate survey object
        s = Survey(row[1], row[2], row[3], row[4], row[5], row[6])                                  

    allQaa = []                                                                                     # Load all the questions from pool. TODO Later only load required questions.
    for r in server.qaaCSV.readRow():                                                               # Questions have to be loaded since they are needed to complete the survey.
        q = Question(1, r[0], r[1:])
        allQaa.append(q)   

    if (request.method == "POST"):                                                                  # At the moment empty responses can be submitted. TODO.
        responses = []
        for i in range(0, s.getNumQuestions()):
            responses.append(request.form[str(i)]) #only store solutions
        surveyResponse = CSV("csv/surveyResponse_"+str(row[0])+".csv")
        surveyResponse.append(responses)                              # Also write the responses into the csv file
        flash("Your response has been recorded")
    return render_template("survey.html", currentSurvey = s, questions = allQaa, valid = valid)

