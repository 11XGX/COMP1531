class Question(object):
    def __init__(self, uniqueID, question, responses):
        self._uniqueID = uniqueID                # To be used later. This will allow the qaa.csv to undergo changes while keep question references consistent.
        self._question = question                # The text/string of the question
        self._responses = responses              # A list of strings for each response to the question

    def getID(self):
        return self._uniqueID

    def getQuestion(self):
        return self._question

    def getResponses(self):
        return self._responses

    def getNumResponses(self):
        return len(self._responses)

    def getCSVRow(self):                        # Creates a printout of this question object's information in a list format so that it may be communicated to other modules.
        qaa = []
        qaa.append(self._question)
        for response in self._responses:
            qaa.append(response)
        return qaa
