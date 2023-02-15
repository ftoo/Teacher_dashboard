#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 11:13:45 2022

@author: faithtoo
"""

  
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)
#................................... data loading and cleaning......................................................................


#load the questions data


questions = pd.read_csv("/Users/faithtoo/Desktop/fellowship/angaza/teacher/data2/quizq_questions.csv",sep=';')
questions.rename(columns={"id": "question_id"}, inplace=True)
questions.drop(["option_a","option_a_explanation","option_b","option_b_explanation","option_c","option_c_explanation","option_d","option_d_explanation","answer","additional_notes","user_id","question_type","created_at","updated_at"],axis=1,inplace=True)
questions.drop(questions[questions.question_level == "L"].index, inplace=True)
questions = questions.drop_duplicates()


#load the class data
classes = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data2/classes.csv',sep=';')
classes.rename(columns={"id": "class_id"}, inplace=True)
classes.drop(["created_at","updated_at"],axis=1,inplace=True)

#load the subjects data
subjects = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data2/subjects.csv',sep=';')
subjects.rename(columns={"id": "subject_id"}, inplace=True)
subjects.drop(["created_at","updated_at"],axis=1,inplace=True)


#load the topics data
topics = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data2/topics.csv',sep=';')
topics.drop(["created_at","updated_at","learning_system"],axis=1,inplace=True)
topics.rename(columns={"id": "topic_id"}, inplace=True)

#load the subtopics data
subtopics = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data2/subtopics.csv',sep=';')
subtopics.rename(columns={"id": "subtopic_id"}, inplace=True)
subtopics.drop(["updated_at"],axis=1,inplace=True)


# merge topics and subjects data
topics_subjects_merger = pd.merge(topics,subjects,on='subject_id',how='left')

# merge subtopics and subjects and topics data

subtopics_topics_subjects_merger = pd.merge(subtopics,topics_subjects_merger,on='topic_id',how='left')
subtopics_topics_subjects_merger.drop(["subject_id_x","class_y"],axis=1,inplace=True)
subtopics_topics_subjects_merger.rename(columns={"class_x": "class_id","subject_id_y": "subject_id"}, inplace=True)

classes_subtopics_topics_subjects_merger = pd.merge(subtopics_topics_subjects_merger,classes,on='class_id',how='left')
classes_subtopics_topics_subjects_merger.drop(["learning_system"],axis=1,inplace=True)



questions_merger = pd.merge(questions,classes_subtopics_topics_subjects_merger, on='subtopic_id',how='left')
questions_merger.drop(["subject_id_x"],axis=1,inplace=True)
questions_merger.rename(columns={"subject_id_y": "subject_id"}, inplace=True)
questions_merger = questions_merger.dropna(subset=['question_level'])





#................................... END OF data loading and cleaning......................................................................


questions_merger = questions_merger.groupby(['class_name','subject_name','topic_name','subtopic_name','question_level']).size().reset_index(name='counts')

class_dropdown = dcc.Dropdown(options=questions_merger['class_name'].unique(),
                            value= 0)

subject_dropdown = dcc.Dropdown(options=questions_merger['subject_name'].unique(),
                            value= 0)
subtopic_dropdown = dcc.Dropdown(options=questions_merger['subtopic_name'].unique(),
                            value= 110)

app.layout = html.Div(children=[
    html.H1(children='Question distribution per Blooms Taxonomy levels'),
    html.P("class:"),
    class_dropdown,
    html.P("subject:"),
    subject_dropdown,
    html.P("subtopic:"),
    subtopic_dropdown,

    dcc.Graph(id='quiz-graph')
])



@app.callback(
    Output(component_id='quiz-graph', component_property='figure'),
    Input(component_id=class_dropdown, component_property='value'),
    Input(component_id=subject_dropdown, component_property='value'),
    Input(component_id=subtopic_dropdown, component_property='value')
)
def generate_chart(selected_class,selected_subject,selected_subtopic ):
   # filtered_quiz = quiz[quiz['marked'] == selected_mark]
    filtered_questions =  questions_merger.loc[(questions_merger['class_name'] == selected_class ) & (questions_merger['subject_name'] == selected_subject ) & (questions_merger['subtopic_name'] == selected_subtopic ) ]
    filtered_questions['percentage']=((filtered_questions['counts']/filtered_questions['counts'].sum())*100).round(2)

   # fig = px.bar(filtered_quiz, x='question_level', y="counts", color='marked_label', text=filtered_quiz['percentage'].apply(lambda x: '{0:1.2f}%'.format(x)))
    fig  = px.pie(filtered_questions, values='counts', names='question_level' )
   #text=filtered_questions['percentage'].apply(lambda x: '{0:1.2f}%'.format(x))
    return fig



app.run_server(debug=True)