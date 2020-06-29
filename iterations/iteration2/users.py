from abc import ABCMeta, abstractmethod

class User():
    __metaclass__ = ABCMeta
    def __init__(self, username, role):
        self._role = role
        self._username = username
        self._courses = []                      
        self._permissions = {}

    def getRole(self):
        return self._role

    def getUsername(self):
        return self._username

    def addCourse(self, courseObject):
        self._courses.append(courseObject)

    def getCourses(self):
        return self._courses
    
    # Classes that are extended from User() need to have there permissions defined
    @abstractmethod
    def getPermissions(self):
        pass


# Subclasses that extend User() are listed below. Open for extentsion.
class Admin(User):
    def __init__(self, username):
        User.__init__(self, username, "admin")
       
    def getPermissions(self):
        return {"dashboard" : ["createsurvey", "createquestions", "viewsurveys", "viewquestions"], "createsurvey" : [], "createquestions" : [], "viewsurveys" : ["editsurvey", "active", "delete", 1, 2, 3, "doform", "surveyresult"], "modifysurvey" : ["deletecompulsory", "deleteoptional", "addcompulsory", "addoptional", "undeletablequestions", 0, 1], "viewquestions" : [], "doform" : ["unlimited"], "surveyresult" : ["unlimited"]} 


class Staff(User):
    def __init__(self, username):
        User.__init__(self, username, "staff")
       
    def getPermissions(self):
        return {"dashboard" : ["viewsurveys"], "viewsurveys" : ["editsurvey", 2, "surveyresult"], "modifysurvey" : ["deleteoptional", "addoptional", 1], "surveyresult" : [3]}


class Student(User):
    def __init__(self, username):
        User.__init__(self, username, "student")
       
    def getPermissions(self):
        return {"dashboard" : ["viewsurveys"], "viewsurveys" : ["doform", "surveyresult"], "doform" : [], "surveyresult" : [3]}

class Guest(User):
    def __init__(self):
        User.__init__(self, "guest", "guest")
    
    def getPermissions(self):
        return {}
   
