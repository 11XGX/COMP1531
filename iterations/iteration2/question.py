from abc import ABCMeta, abstractmethod

class QuestionHandler(object):
    questionTypes = ["TextQuestion", "MCQ"]                                                                                                         # EXTENSION HERE ON NEW QTYPES
    
    @staticmethod
    # Returns all the questiontypes that exist
    def getAllQuestionTypes():
        return QuestionHandler.questionTypes           

    @staticmethod
    # Creates the question based on the HTML Request Form coming from routes.py
    def newQuestionRequest(key, questionType, request):                                                                                             # EXTENSION HERE ON NEW QTYPES
        compulsory = 1
        if ("optional" in request.form):
            compulsory = 0
        if (questionType == "TextQuestion"):
            return TextQuestion(key, compulsory, request.form["question"]) 
        if (questionType == "MCQ"):
            responses = []
            for i in range(0, len(request.form)):
                if (str(i) in request.form and request.form[str(i)] != ""):
                    responses.append(request.form[str(i)])
            return MCQ(key, compulsory, request.form["question"], responses)
        return 0 

    @staticmethod
    # Creates the appropriately typed question object based on the READ data
    def createTypedQuestion(dataRow):                                                                                                               # EXTENSION HERE ON NEW QTYPES
        if (dataRow[2] == "TextQuestion"):  
            question = TextQuestion(dataRow[0], dataRow[3], dataRow[4])
            question.setAdminAdded(int(dataRow[1]))                                                  
            return question
        if (dataRow[2] == "MCQ"): 
            question = MCQ(dataRow[0], dataRow[3], dataRow[4], dataRow[5:]) 
            question.setAdminAdded(int(dataRow[1]))                                                               
            return question  
        return 0

class Question(object):                         # Question is an abstract class (OCP). Cannot be instantiated - rather objects that inherit from Question must be instantiated.
    __metaclass__ = ABCMeta

    def __init__(self, uniqueID, questionType, compulsory, question):
        self._uniqueID = uniqueID
        self._questionType = questionType
        self._compulsory = compulsory
        self._question = question
        self._adminAdded = 0                    # The 'adminAdded' flag not useful for questions in the questionpool. It becomes useful for questions directly associated with surveys.

    def getID(self):
        return self._uniqueID

    def setAdminAdded(self, boolean):
        self._adminAdded = boolean

    def getAdminAdded(self):
        return self._adminAdded

    def setType(self, questionType):
        if type not in Question.questionTypes:
            return
        self._questionType = questionType

    def getType(self):
        return self._questionType

    def getCompulsory(self):
        return self._compulsory

    def getQuestion(self):
        return self._question

    @abstractmethod
    def getWritableRow(self):
        pass

# A Question object provides a question with no set answers.
class TextQuestion(Question):

    def __init__(self, uniqueID, compulsory, question):
        Question.__init__(self, uniqueID, "TextQuestion", compulsory, question)   

    def getWritableRow(self):                     # Creates a printout of this question object's information in a list format so that it may be communicated to other modules.
        qaa = []
        qaa.append(self._uniqueID)
        qaa.append(self._adminAdded)
        qaa.append(self._questionType)
        qaa.append(self._compulsory)
        qaa.append(self._question)
        return qaa

# A MCQ object extends on a question object. MCQ objects do have set answers.
class MCQ(Question):

    def __init__(self, uniqueID, compulsory, question, responses):
        Question.__init__(self, uniqueID, "MCQ", compulsory, question)
        self._responses = responses               # A list of strings for each response to the question

    def getResponses(self):
        return self._responses

    def getNumResponses(self):
        return len(self._responses)

    def getWritableRow(self):
        qaa = []
        qaa.append(self._uniqueID)
        qaa.append(self._adminAdded)
        qaa.append(self._questionType)
        qaa.append(self._compulsory)
        qaa.append(self._question)
        for response in self._responses:
            qaa.append(response)
        return qaa     

