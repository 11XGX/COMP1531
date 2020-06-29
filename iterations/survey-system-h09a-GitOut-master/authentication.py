"""
File: authentication.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: The 'authentication module" is part of the logic/business tier
             and is called from a controller (routes.py).
"""

# Imported libraries...
import hashlib
import server
from users import User, Admin, Staff, Student, Guest, Unassigned
import csv

user_role = "guest"

# This function is used to validate a user login when trying to access the survey system.
def login(userID, password):
    global user_role
    session = server.DBSession()


    # A user will enter a query in which their username and password need to be validated.
    user = session.query(User).filter(User.username==userID).first()
    # Then load the user into an appropriate subclass
    if (user != None):
        user = session.query(eval(user.role.title())).filter(User.username==userID).first()
    session.close()

    # If the entered username or password is wrong, logout and return an error.
    if (user == None or user.password != password):
        logout()
        return -1
    # If the user is still pending approval as a guest, logout and return.
    if (user.role == "unassigned"):
        logout()
        return 0

    server.user = user
    user_role = user.role
    return user

# This function reloads the user from the database.
def forceLogin(userId):
    global user_role
    session = server.DBSession()

    # Access the username from the database.
    user = session.query(User).filter(User.username==userId).first()
    user = session.query(eval(user.role.title())).filter(User.username==userId).first()
    session.close()

    # Print their user role.
    server.user = user
    print(server.user.role)
    user_role = user.role

# This function is used to logout a user from the survey system.
def logout():
    # Reinitalises the user role, revokes their authentication and resets their access to the server.
    global user_authenticated, user_role
    user_role = "unassigned"
    server.user = Unassigned()

# NOTE: Specifications say that this should be handled in the authentication module.
# This function handles the creation of a guest user account.
def createGuestRequest(userId, password, courseName):
    session = server.DBSession()
    user = session.query(User).filter(User.username == userId).first()
    if (user != None or user == '' or password == '' or courseName == ''):
        return -1

    u = User()
    u.username = userId
    u.password = password
    # The user role is changed to guest upon approval of their request.
    u.role = "unassigned"
    u.courses = [courseName]
    u.surveysResponded = []
    u.authenticated = False

    session.add(u)
    session.commit()
    session.close()
    return 1

