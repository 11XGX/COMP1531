class Course(object):
    def __init__(self, name):
        self._name = name

    def getName(self):
        return self._name

class SessionOffering(Course):
    def __init__(self, name, session):
        Course.__init__(self, name)
        self._session = session
        self._survey = 0
        
    def getSession(self):
        return self._session

    # Associates the survey object to this course. Must save the course to external file after this change for persistence.
    def addSurvey(self, survey):
        self._survey = survey

    # Gets the currently associated survey object for this course.
    def getSurvey(self):
        return self._survey
    
    # Removes the associated survey object from this course. Must save the course to external file after this change for persistence.
    def removeSurvey(self):
        self._survey = 0

