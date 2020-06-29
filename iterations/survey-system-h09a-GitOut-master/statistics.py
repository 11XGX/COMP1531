"""
File: statistics.py
Date: 12 October 2017
Author(s): GitOut 2017 COMP1531 Group Project
Description: This function deals with the display of survey results.
             Either in the form of a pie chart OR table depending on the type of question.
"""

# Imported libraries...
import plotly
from plotly.graph_objs import Scatter, Layout, Pie
import plotly.figure_factory

# This function creates a single pie chart displaying:
# - The survey question as a string (e.g. "What is your name?").
# - The survey responses as a list of values with a number attached, corresponding to the number of selections for that choice.
# NOTE: This is used for questions with multiple-choice responses.
def createPieChart(surveyQuestion, surveyResponses):
    print(surveyResponses)
    # A label for each possible response...
    labels = []
    values = []
    for response in surveyResponses:
        if response not in labels and response != "":
            # Create a label for each response not read before.
            labels.append(response)
            # Initialise the value corresponding to the new label to 1.
            values.append(1)
        elif response != "":
            values[labels.index(response)] += 1
    trace = Pie(labels = labels, values = values)
    return (plotly.offline.plot([trace], include_plotlyjs=False, output_type='div'))

  
# This function creates a table displaying:
# - The survey question as a string (e.g. "What is your name?").
# - The survey responses as a list of responses to that question (e.g. ["Jess", "Jane"]).
# NOTE: This is used for questions with text-based responses.
def createTable(surveyQuestion, surveyResponses, question):
    print(surveyResponses)
    answers = [[question]]
    for response in surveyResponses:
        if response != "":
            answers.append([response])
    trace = plotly.figure_factory.create_table(answers)
    return(plotly.offline.plot(trace, include_plotlyjs=False, output_type='div'))
