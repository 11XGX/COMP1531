from flask import Flask, redirect, request, render_template, url_for
from flask_login import LoginManager,login_user, current_user, login_required, logout_user
from model import User
from server import app, login_manager

# Password checking and logging in the user if the given
# password matches the given user's password.
def check_password(user_id, password):
    if password == "admin_password":
        user = User(user_id)
        login_user(user)

        return True
    return False
    
# Get the user's details from the database.
def get_user(user_id):
    return User(user_id)
    

# Get the user's information from the database.
@login_manager.user_loader
def load_user(user_id):
    user = get_user(user_id) 
    return user
    
# Routing logic:
@app.route('/',methods=["GET","POST"])
def login():
    if request.method == "POST":
        user_id = int(request.form["zid"])
        password = request.form["password"]
        
        if check_password(user_id, password):
            return redirect(url_for('index'))
    return render_template("basic_login.html")
    
# Routing logic:
@app.route('/index')
@login_required
def index():
    return render_template("logged.html")
    
# Logging out the user:
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
    
if __name__=="__main__":
    app.run(debug=True)
