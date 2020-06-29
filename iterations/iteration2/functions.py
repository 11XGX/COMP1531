# Helper functions so that routes.py does not become cluttered with indirect funcions

from courses import Course, SessionOffering
from survey import Survey
from question import QuestionHandler, Question, TextQuestion, MCQ
from fileReader import CSVReader
from fileWriter import CSVWriter
import server
import random
import string
import os.path

# Loads in all sessionOfferings from file into course/session objects. Associates any survey forms to that session offering if the association exists.
def loadAllCourseObjects(reader):
    courseList = reader.readAllRows()                                                       # Read the given courses.csv file to determine currently available courses
    courseObjects = []
    for course in courseList:                                                         
        courseObjects.append(SessionOffering(course[0], course[1]))
        if (len(course) > 2):
            # load the survey object and associate it with the course
            loadedSurvey = loadSurvey(course[2])
            if (loadedSurvey != 0):
                courseObjects[len(courseObjects)-1].addSurvey(loadedSurvey)                 # Only one survey key per course offering
    return courseObjects   

# Modifies the course in the courses file (compound key of course name + session). Associates this course with the given survey key
def associateCourse(reader, writer, compoundKey, surveyKey):
    currentRow = reader.readCompoundKeyedRow(compoundKey)
    if (len(currentRow) > 2): 
        currentRow[2] = surveyKey                                                           # Overwrite the current survey associated with this course if there is one
    else:
        currentRow.append(surveyKey)
    writer.replaceCompoundKeyedRow(reader, compoundKey, currentRow)

# Reads the enrolment file and adds on course offerings for the given user to that user's object.
# Also loads the neccessary survey objects and associates them to the loaded courses by reading the courses file.
def coursesToUser(sessionReader, courseReader, userObject):
    userEnrolments = sessionReader.readKeyedRow(str(userObject.getUsername()))
    for i in range (0, int(len(userEnrolments) / 3)):                                       # More than one enrolment for user possible. Each enrolment row is 3 entries
        course = SessionOffering(userEnrolments[3*i+1], userEnrolments[3*i+2])
        compoundKey = [userEnrolments[3*i+1], userEnrolments[3*i+2]]
        courseFile = courseReader.readCompoundKeyedRow(compoundKey)
        if (len(courseFile) > 2):                                                           # Then the row has a third entry (etc. the survey key)
            loadedSurvey = loadSurvey(courseFile[2])                                                           
            course.addSurvey(loadedSurvey)
        userObject.addCourse(course)

# Checks if a specific user has completed a specific survey by searching through respondents file (respondents.csv)
def userHasRespondedSurvey(respondentsReader, username, surveyKey):
    if not os.path.exists(respondentsReader.getFile()):
        return
    for row in respondentsReader.readAllRows():
        if (str(row[0]) == str(username)) and (str(row[1]) == surveyKey):
            return True
    return False

# Same as above except handles a list of courses and returns a list of booleans. Uses above function in a loop
def userHasRespondedSurveys(respondentsReader, username, courses):
    responseRegistered = []
    for course in courses:
        if course.getSurvey() != 0:
            responseRegistered.append(userHasRespondedSurvey(respondentsReader, username, course.getSurvey().getKey()))
        else: 
            responseRegistered.append(-1)
    return responseRegistered

# Checks if a spefic user is allowed to access a survey with the given key. Checks this by looking at the courses associated with the userObject and is any of those courses have 
# a matching key to the survey
def userCanParticiplate(userObject, surveyKey):
    for course in userObject.getCourses():
        if (course.getSurvey() != 0 and course.getSurvey().getKey() == surveyKey):
            return True
    return False

# Write the new question into qaa file. 
def saveNewQuestion(writer, question):
    writer.append(question.getWritableRow()) 

# Loads in all questions from questionpool into question objects
def loadAllQuestions(reader):
    allQaa = []                                                                             # Read every question in pool from the csv into question objects. Neccessary here.
    for row in reader.readAllRows():
        allQaa.append(QuestionHandler.createTypedQuestion(row))     
    return allQaa 

# Loads in only all optional questions from questionpool into question objects
def loadOptionalQuestions(reader):
    optionalQ = []
    for row in reader.readAllRows():
        if int(row[3]) == 0:
            optionalQ.append(QuestionHandler.createTypedQuestion(row))
    return optionalQ

# Loads in only questions from questionpool into question objects if they have one of the given keys passed in keyList[]
def loadKeyedQuestions(reader, keyList):
    foundQuestions = []
    for key in keyList:
        for row in reader.readAllRows():
            if row[0] in str(key):
                foundQuestions.append(QuestionHandler.createTypedQuestion(row))  
    return foundQuestions    

# Same as above, except loads only one question
def loadKeyedQuestion(reader, key):
    for row in reader.readAllRows():
        if row[0] in str(key):
            return QuestionHandler.createTypedQuestion(row)
    return 0

# Finds the question with a specific key from a pool of questions. Returns 0 if not found. Otherwise returns question object.
def findKeyedQuestion(key, questionPool):
    for question in questionPool:
        if question.getID() == key:
            return question
    return 0

# Finds the question given the row number of the question in file. Returns 0 if invalid row. Otherwise returns question key.
# Finding a row should not be relied on upon different HTML pages, since a question may be deleted and hence row changed.
def findRowedQuestion(reader, row):
    allRows = reader.readAllRows()
    if (row >= len(allRows)):
        return 0 
    return allRows[row][0]

# Returns a list containing the row number of the question corresponding to the given list of survey keys. etc. keyList = ["key1", "key2"]. return = [1, 0].
# Should not rely on row numbers to remain consistent across HTML pages.
def findRowKeyedQuestions(reader, keyList):
    rowList = []
    for key in keyList:
        found = 0
        rowCount = 0
        for row in reader.readAllRows():
            if row[0] in key:
                found = 1
                rowList.append(rowCount)
            rowCount += 1
        if (not found):
            rowList.append(-1)
    return rowList

# Finds the row in the questionpool file with the given key and deletes that row from the questionpool table/file
def deleteQuestion(questionWriter, questionReader, key):
    questionWriter.deleteRow(questionReader, key)

# Writes/Overwrites a surveyForm file. Each survey has it's own surveyForm that contains session information associated to that survey
# as well as all the questions associated with the survey. This is required as questions removed from the questionPool are required to persist in surveyForms.  
def writeSurvey(surveyWriter, questionReader, survey, questionList):
    if os.path.exists(surveyWriter.getFile()):                                                      # Remove the survey form if it already exists
        os.remove(surveyWriter.getFile())
    surveyWriter.append(survey.getWritableRow())                                                    # Top line of the survey form is name, desc, surveyKey etc.
    for question in questionList:            
        surveyWriter.append(question.getWritableRow())                                              # Write each question into survey form in own row
    return 1          

# Returns a survey object that corresponds to the file that the reader has opened. Returns 0 if reader has read an empty file.
def loadSurvey(key):
    if not os.path.exists("csv/surveyform_"+str(key)+".csv"):
        return 0
    reader = CSVReader("csv/surveyform_"+str(key)+".csv")
    rows = reader.readAllRows()  
    if (rows != []):
        loadSurvey = Survey(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5]) # The first row of the read surveyForm file is data about the session 
        return loadSurvey
    return 0

# Loads the questions from the survey form. Not loaded from the question pool, since questions used in survey may be deleted from pool but required to persist in survey.
def loadSurveyQuestions(key):
    if not os.path.exists("csv/surveyform_"+str(key)+".csv"):
        return 0
    reader = CSVReader("csv/surveyform_"+str(key)+".csv")
    rows = reader.readAllRows()
    surveyQuestions = []
    for i in range (1, len(rows)):
        foundQuestion = QuestionHandler.createTypedQuestion(rows[i])
        if (foundQuestion != 0):
            surveyQuestions.append(foundQuestion)
    return surveyQuestions

# Check if the given survey has any recorded responses
def hasResponses(surveyKey):
    if not os.path.exists("csv/surveyresponse_"+str(surveyKey)+".csv"):
        return 0
    return 1  

# Toggles the 'activate' flag for the given survey and then saves it to file (csv)
def activateToggleSurvey(survey):
    survey.alternateActive()  
    surveyQuestions = loadSurveyQuestions(survey.getKey())
    writeSurvey(CSVWriter("csv/surveyform_"+survey.getKey()+".csv"), server.qaaCSVReader, survey, surveyQuestions)

# Adds a number to the 'phase' flag for the given survey adn then saves it to file (csv)
def nextPhaseSurvey(survey):
    survey.setPhase(int(survey.getPhase()) + 1)
    if (survey.getPhase() >= 2):                                                            # Automatically toggle 'active' on if "open" phase and toggle off if "closed" phases
        survey.alternateActive()                                                            # Survey master active switch turned on if pushed to 'open' phase
    surveyQuestions = loadSurveyQuestions(survey.getKey())
    writeSurvey(CSVWriter("csv/surveyform_"+survey.getKey()+".csv"), server.qaaCSVReader, survey, surveyQuestions)

# Deletes the survey with the given key from the file. If there are any survey objects loaded they will persist until reload from file.
# Also deletes that survey key from being associated with any courses it was associated with
def deleteSurvey(courseReader, courseWriter, session, key):
    if os.path.exists("csv/surveyform_"+str(key)+".csv"):                                           # Remove the surveyform (csv) if it exists
        os.remove("csv/surveyform_"+str(key)+".csv")
    session.removeSurvey()                                                                          # Removes survey from currently loaded session object
    courseWriter.deleteEntries(courseReader, key)                                                   # Removes survey key written in the courses file

def randomKey():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))

