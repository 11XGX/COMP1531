import plotly
from plotly.graph_objs import Scatter, Layout, Pie

# Creates one pie chart 
# surveyQuestion is the question strings etc. "What is your name?"
# surveyResponses is a list of all responses to that question etc. ["Jesse", "Jane"]
def createPieChart(surveyQuestion, surveyResponses):
    print(surveyResponses)
    labels = []  
    values = []                                                                 # A label for each possible response
    for response in surveyResponses:
        if response not in labels and response != "":
            labels.append(response)                                             # Create a label for each response we have not seen before
            values.append(1)                                                    # Initialise value corresponding to this new label to 1
        elif response != "":
            values[labels.index(response)] += 1  

    trace = Pie(labels = labels, values = values)
    return (plotly.offline.plot([trace], include_plotlyjs=False, output_type='div'))
