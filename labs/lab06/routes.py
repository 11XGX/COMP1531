from flask import Flask, redirect, render_template, request, url_for
from server import app
from math import *

userInput = ""
@app.route("/", methods=["GET", "POST"])                    # Flask
def index():
    global userInput
    buttons = [["1", "2", "3", "C"], ["4", "5", "6", "+"], ["7", "8", "9", "-"], ["0", "*", "/", "="], ["(", ")", "sin", "tan"], ["cos", "log", "sqrt", "CE"]]
    if request.method == "POST":
        if (request.form["bt"] == "="):
            userInput = str(eval(userInput))
        elif (request.form["bt"] == "C"):
            userInput =  userInput[0 : len(userInput) - 1]
        elif (request.form["bt"] == "CE"):
            userInput = ""
        else:
            userInput = userInput + request.form["bt"]
    return render_template("index.html", buttons = buttons, userInput = userInput)
