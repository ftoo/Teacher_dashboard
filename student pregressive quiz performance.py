#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 22:10:57 2023

@author: faithtoo
"""


  
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np


app = Dash(__name__)


#................................... data loading and cleaning......................................................................


#load the questions data
questions = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data/quizq_questions.csv',sep=';')

questions.rename(columns={"id": "question_id"}, inplace=True)
questions.drop(["option_a","option_a_explanation","option_b","option_b_explanation","option_c","option_c_explanation","option_d","option_d_explanation","answer","additional_notes","user_id","question_type","created_at","updated_at"],axis=1,inplace=True)
questions = questions.drop_duplicates()

#load the quiz data
quiz = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data/question_answers.csv',sep=';')
quiz = quiz.drop_duplicates()

# merge quiz and questions data
quiz_questions = pd.merge(quiz,questions,on='question_id',how='left')
quiz_questions.drop(["answer","created_at","assigned_marks","subtopic_id_y","subject_id_y"],axis=1,inplace=True)
quiz_questions.rename(columns={"subject_id_x": "subject_id","subtopic_id_x": "subtopic_id"}, inplace=True)
quiz_questions.drop(quiz_questions[quiz_questions.question_level == "L"].index, inplace=True)

#load the class data
classes = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data/classes.csv',sep=';')
classes.rename(columns={"id": "class_id"}, inplace=True)
classes.drop(["created_at","updated_at"],axis=1,inplace=True)

#load the subjects data
subjects = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data/subjects.csv',sep=';')
subjects.rename(columns={"id": "subject_id"}, inplace=True)
subjects.drop(["created_at","updated_at"],axis=1,inplace=True)


#load the topics data
topics = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data/topics.csv',sep=';')
topics.drop(["created_at","updated_at","learning_system"],axis=1,inplace=True)
topics.rename(columns={"id": "topic_id"}, inplace=True)

#load the subtopics data
subtopics = pd.read_csv('/Users/faithtoo/Desktop/fellowship/angaza/teacher/data/subtopics.csv',sep=';')
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



quiz_questions_merger = pd.merge(quiz_questions,classes_subtopics_topics_subjects_merger, on='subtopic_id',how='left')
quiz_questions_merger.drop(["subject_id_x"],axis=1,inplace=True)
quiz_questions_merger.rename(columns={"subject_id_y": "subject_id"}, inplace=True)
quiz_questions_merger = quiz_questions_merger.dropna(subset=['question_level'])

quiz_questions_merger['marked_label'] = np.where(quiz_questions_merger['marked'] == 0, 'Incorrect', 'Correct')

quiz_questions_merger['total_marks'] = quiz_questions_merger.groupby(['quiz_id'])['question_id'].transform('nunique')
quiz_questions_merger['score'] = ((quiz_questions_merger.groupby(['quiz_id'])['marked'].transform('sum'))/quiz_questions_merger['total_marks']*100).round(2)
quiz_questions_merger['quiz_id'] = quiz_questions_merger['quiz_id'].replace('0','null')
quiz_questions_merger.drop(quiz_questions_merger[quiz_questions_merger.quiz_id == "null"].index, inplace=True)


#................................... END OF data loading and cleaning......................................................................


quiz= quiz_questions_merger.groupby(['student_id','class_name','subject_name','topic_name','subtopic_name','quiz_id','updated_at'])["score"].mean()
quiz= quiz.reset_index()



student_dropdown = dcc.Dropdown(options=quiz['student_id'].unique(),
                            value= 0)
topic_dropdown = dcc.Dropdown(options=quiz['topic_name'].unique(),
                            value= 0)


app.layout = html.Div(children=[
    html.H1(children='Quiz performance Progression'),
    html.P("Student:"),
    student_dropdown,
    html.P("Topic:"),
    topic_dropdown,
    dcc.Graph(id='progression-chart')
])



@app.callback(
    Output(component_id='progression-chart', component_property='figure'),
    Input(component_id=student_dropdown, component_property='value'),
    Input(component_id=topic_dropdown, component_property='value')

)
def generate_chart(selected_student, selected_topic):

    filtered_student =  quiz.loc[(quiz['student_id'] == selected_student )& (quiz['topic_name'] == selected_topic )]

    filtered_student = filtered_student.drop_duplicates(subset='quiz_id', keep="first")

    fig = px.bar(filtered_student, x='quiz_id', y='score', color='subtopic_name', text=filtered_student['updated_at'])
    fig.update_traces(width=1)

    return fig



app.run_server(debug=True)