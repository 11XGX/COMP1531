"""
File: run.py
Date: 05 September 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This runs the survey system from routes.py.
"""

# Imported libraries...
from routes import app
import server

app.run(debug=True)
