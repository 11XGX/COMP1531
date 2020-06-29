from flask import Flask, redirect, render_template, request, url_for
from server import app

sort = []

@app.route("/", methods=["GET", "POST"])                    # Flask
def index():
    global sort
    if request.method == "POST":
        sort = request.form["numbers"].split(',')
        sort = bubblesort(sort)
    return render_template("index.html", toSort = sort)
            
def bubblesort(numbers):
    steps = []
    steps.append(numbers[:])
    for i in range(len(numbers)):
        for j in range(len(numbers) - 1, i, -1):
            if (numbers[j] < numbers[j - 1]):
                temp = numbers[j]
                numbers[j] = numbers[j - 1]
                numbers[j - 1] = temp
                steps.append(numbers[:])
    return steps
