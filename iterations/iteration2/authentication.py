# The 'Authentication Module'. 
# Authentication is part of the logic/business tier. 
# Called from controller (routes.py). 

import hashlib

user_role = "guest"	

def login(reader, userID, password):
    global user_role
    data = reader.readKeyedRow(userID)                  # readKeyedRow will return the items on row with matching key as list. -1 if unsuccessful.
    if ((data != []) and (password == data[1])):        # If key is found and matching password provided then user logged in appropriately.
        user_role = data[2]
        return 1                                        # Return 1 on successful login
    logout();                                           # Else, effectively logout and return 0 for failed login
    return 0                                            

def logout():
    global user_authenticated, user_role
    user_role = "guest"
