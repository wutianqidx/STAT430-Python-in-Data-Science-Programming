# -*- coding: utf-8 -*-
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Read in GPA dataset
gpa = pd.read_csv('https://raw.githubusercontent.com/wadefagen/datasets/master/gpa/uiuc-gpa-dataset.csv')

# Remove missing value (155 out of 53933)
gpa = gpa[gpa.notna().all(1)].reset_index()

# Drop unused columns
gpa = gpa.drop(['index', 'Year', 'Term', 'YearTerm', 'Course Title'], axis = 1)

# Convert letter grade
gpa['As'] = gpa['A+'] + gpa['A'] + gpa['A-']
gpa['Bs'] = gpa['B+'] + gpa['B'] + gpa['B-']
gpa['Cs'] = gpa['C+'] + gpa['C'] + gpa['C-']
gpa['Ds'] = gpa['D+'] + gpa['D'] + gpa['D-']
gpa['Fs'] = gpa['F']

# Calculate total GPA
gpa['grade'] = 4*(gpa['A+'] + gpa['A']) + 3.67*gpa['A-'] + 3.33*gpa['B+'] + \
                3*gpa['B'] + 2.67*gpa['B-'] + 2.33*gpa['C+'] + 2*gpa['C'] + \
                1.67*gpa['C-'] + 1.33*gpa['D+'] + 1*gpa['D'] + 0.67*gpa['D-']

# Get total number of students
gpa['Students'] = gpa.iloc[:, 2:15].sum(1)

# Drop unused columns
gpa = gpa.drop(gpa.columns[list(range(2,16))], axis = 1)

# Group by subject, number and instructor
gpa = gpa.groupby(['Subject', 'Number', 'Primary Instructor']).agg([('sum')])
gpa = gpa.reset_index()
gpa.columns = gpa.columns.droplevel(1)

# Calculate average GPA
gpa['Avg.GPA'] = round(gpa['grade'] / gpa['Students'], 2)

# Get dropdown options for subjects
available_subject = gpa['Subject'].unique()

app.layout = html.Div([

	html.H6("Grade difference between different sections for UIUC"),

	html.Div([	"Subject:",
				dcc.Dropdown(
        		id='subjects-dropdown',
        		options=[{'label': i, 'value': i} for i in available_subject],
        		value='AAS')], 
				style={'width': '48%', 'display': 'inline-block'}),

    html.Hr(),

	html.Div([	"Number:",
    			dcc.Dropdown(id='numbers-dropdown')], 
				style={'width': '48%', 'display': 'inline-block'}),

	dcc.Graph(id='gpa-graphic'),
])


@app.callback(
    Output('numbers-dropdown', 'options'),
    Input('subjects-dropdown', 'value'))
def set_number_options(selected_subject):
	available_number = gpa.loc[gpa.Subject == selected_subject, 'Number'].unique()
	return [{'label': i, 'value': i} for i in available_number]


@app.callback(
    Output('numbers-dropdown', 'value'),
    Input('numbers-dropdown', 'options'))
def set_number_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('gpa-graphic', 'figure'),
    Input('subjects-dropdown', 'value'),
    Input('numbers-dropdown', 'value'))

def update_graph(selected_subject, selected_number):
	# Filter with selected subject and course number and sort by average GPA
	selected_course = gpa.loc[(gpa.Subject == selected_subject) & (gpa.Number == selected_number)].sort_values('Avg.GPA')

	# Prevent update if dataframe is empty
	if len(selected_course) == 0:
		raise dash.exceptions.PreventUpdate

	fig = px.bar(selected_course, x=['As', 'Bs', 'Cs', 'Ds', 'Fs'], y="Primary Instructor",
             title=selected_subject + str(selected_number), hover_name = 'Primary Instructor', 
             hover_data = {'Primary Instructor':False, 'Avg.GPA':True},
             orientation='h', labels = dict(value='Number of Students', variable = 'Letter Grade'))

	fig.update_layout(yaxis= dict(dtick = 1), legend_title="Letter Grade")

	return fig
   


if __name__ == '__main__':
    app.run_server(debug=True)
