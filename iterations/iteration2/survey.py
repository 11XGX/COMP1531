class Survey(object):                   
    def __init__(self, key, active, phase, name, desc, questions):
        self._key = key                
        self._active = active                       # 'Master' switch for the survey. 
        self._phase = phase                         # Phase is per specifications. Phase 0 is admin access only, phase 1 admin+staff access, phase 2 admin+staff+student access
        self._name = name
        self._desc = desc
    
        if(isinstance(questions, list)):            # If the given questions argument is a list, then simply assign it to self._questions
            self._questions = questions             # Else the given question argument is a string and should be split about "," chars
        else:
            temp = questions.replace("[", "").replace("]", "").split(",");
            if(len(temp) <= 1 and temp[0] == ''):
                temp = ['0']                        # Add initial question if it is empty
            self._questions = list(map(str, temp))  # A list of the questionID's (or it will/should be). At the moment it is the row it can be found in qaa.csv.              

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

    def getPhase(self):
        return self._phase

    def setPhase(self, phase):
        self._phase = phase

    def getName(self):
        return self._name
    
    def getDesc(self):
        return self._desc

    def addQuestion(self, questionID):
        self._questions.append(questionID)

    def removeQuestion(self, questionID):
        self._questions.remove(questionID)

    def getQuestions(self):
        return self._questions

    def clearQuestions(self):
        self._questions.clear()

    def getNumQuestions(self):
        return len(self._questions)

    def getWritableRow(self):                         # Creates a list of the current survey attributes - to communiate information about this survey in a list format to other modules.
        csvRow = []
        csvRow.append(self._key)
        csvRow.append(self._active)
        csvRow.append(self._phase)
        csvRow.append(self._name)
        csvRow.append(self._desc)
        temp = str(self._questions).replace("/","").replace('"',"").replace(" ","")
        csvRow.append(temp)
        return csvRow

