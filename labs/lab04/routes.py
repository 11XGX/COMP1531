from flask import Flask, redirect, render_template, request, url_for
from server import app
import csv

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        zID = int(request.form["zID"])
        desc = request.form["desc"]
        
        with open('info.csv','a') as csv_out:
            writer = csv.writer(csv_out)
            writer.writerow([name, zID, desc])

        return redirect(url_for("hello"))
    return render_template("index.html")

@app.route("/Hello")
def hello():
    user_input = []
    with open('info.csv','r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            user_input.append(row)
    return render_template("hello.html", all_users=user_input)
