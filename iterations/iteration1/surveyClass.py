class Survey(object):                   
    def __init__(self, key, active, course, name, desc, questions):
        # Construct a survey object with the given parameters
        self._key = key                
        self._active = active
        self._course = course
        self._name = name
        self._desc = desc
    
        # If the given questions argument is a list, then simply assign it to self._questions
        # Else the given question argument is a string and should be split about "," chars
        if(isinstance(questions, list)):
            self._questions = questions
        else:
            temp = questions.replace("[", "").replace("]", "").split(",");
            if(len(temp) <= 1 and temp[0] == ''):
                temp = ['0'] #add initial question if it is empty

            self._questions = list(map(int, temp))              # A list of the questionID's (or it will/should be). At the moment it is the row it can be found in qaa.csv.              
    
    def getKey(self):
        return self._key

    def getActive(self):
        return int(self._active)

    def setActive(self, flag):
        self._active = int(flag)
    
    def alternateActive(self):
        if int(self._active) == 1:
            self._active = 0
        else:
            self._active = 1

    def getCourse(self):
        return self._course

    def getName(self):
        return self._name
    
    def getDesc(self):
        return self._desc

    def addQuestion(self, questionID):
        self._questions.append(int(questionID))

    def getQuestions(self):
        return self._questions

    def clearQuestions(self):
        self._questions.clear()

    def getNumQuestions(self):
        return len(self._questions)

    def getCSVRow(self):                         # Creates a printout of the current survey - to communiate information about this survey in a list format to other modules.
        csvRow = []
        csvRow.append(self._key)
        csvRow.append(self._active)
        csvRow.append(self._course)
        csvRow.append(self._name)
        csvRow.append(self._desc)
        csvRow.append(self._questions)
        #for question in self._questions:
        #    csvRow.append(question)
        return csvRow
