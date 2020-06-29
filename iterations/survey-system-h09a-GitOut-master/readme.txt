--- Section 1 ---
External Python libraries being used are:
    Flask and Jinja - These libraries were used for the web development and templating for the survey system.

    SQLAlchemy - SQLAchemy was used for the database layer of this project. This package allowed 
        Object Relational Mapping database functionality through the Python language.

    Plotly - This libary was used to draw the pie graphs and tables for the different question types.
        Such graphs were used to present the responses to the surveys in the system.

    Numpy - This aided in scientific and mathematical computation. 
    Pytest - For running the python tests contained in tests.zip. See Section 3 below.


--- Section 2 ---
To run the application:
   Go to the  working directory while inside the python virual environment.
   Run pip3 install to install all of the required libraries/packages. These packages are listed in requirements.txt. 
   Once the above is done, launch the terminal from the working directory, where all project files are located.
   In terminal, type "python3 run.py". This is typed without the quote marks.  
   This will run the server at: http://localhost:5000/

   Open any web-browser and navigate to the above address.
   Note that on first run of the application there may be some delay as the database is built.


--- Section 3 ---
To run the test files:
   Extract the tests.zip folder into the main application folder.
   Run each test file using pytest "TESTNAME". Where TESTNAME is replaced by the specific name of the test less the quotes. 
   etc. python3 test_enrol.py
   etc. pytest test_enrol.py
   Either of the above should work.
   This will run the test specified and print the outcome. 

   Running all tests can be done by typing "pytest" if installed.
   A summary of which tests passed/failed is printed to terminal along with any detailed error messages.
