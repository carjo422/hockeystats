#Establish connection to database

import os

if os.path.exists('/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/'):
    data_directory = '/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/'
else:
    data_directory = '/Users/carljonsson/Python/hockeystats/'

import sqlite3
conn = sqlite3.connect(data_directory + '/hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from pandas import ExcelWriter
import pickle
from create_pre_match_tables import update_model1_data
from create_pre_match_tables import update_model2_data
from model_evaluation_scoring import evaluate_scoring_model


def update_goal_scorer(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT * FROM EXP_GOAL_SCORER WHERE SEASONID < ?",[2019])
    regdata = pd.DataFrame(c.fetchall(),columns=['Serie', 'Season', 'Team', 'Gameid', 'Gamedate', 'Forname', 'Surname', 'Personnr','Age', 'Position', 'Last_Line', 'Handle', 'Pos_Score', 'Pos_Score_Last','Pos_Multiplier', 'Hist_Scoring', 'Score_Ratio', 'Hist_Scoring_REG', 'Hist_Scoring_PP','In_PP', 'Trend', 'Weight', 'Act_Goal', 'Exp_Goal'])

    regdata['Pos_Score_Final'] = regdata['Pos_Score'] * regdata['Pos_Multiplier']
    regdata['Pos_Score_Final_Last'] = regdata['Pos_Score_Last'] * regdata['Pos_Multiplier']
    regdata['Hist_Scoring_Reg_Final'] = (regdata['Score_Ratio'] * regdata['Hist_Scoring_REG']*regdata['Weight'] + regdata['Pos_Score_Final'] * 5) / (regdata['Weight']+5)
    regdata['Hist_Scoring_PP_Final'] = (regdata['Hist_Scoring_PP'] * regdata['Weight'] + regdata['Pos_Score_Final'] * 5) / (regdata['Weight']+5)

    #Model 1 inputs

    x_model1 = regdata[['Pos_Score_Final','Pos_Score_Final_Last','Hist_Scoring']]
    y_model1 = regdata['Act_Goal']

    #Model 2 Inputs


    # Test data

    c.execute("SELECT * FROM EXP_GOAL_SCORER WHERE SEASONID >= ?", [2019])
    testdata = pd.DataFrame(c.fetchall(),columns=['Serie', 'Season', 'Team', 'Gameid', 'Gamedate', 'Forname', 'Surname', 'Personnr','Age', 'Position', 'Last_Line', 'Handle', 'Pos_Score', 'Pos_Score_Last','Pos_Multiplier', 'Hist_Scoring', 'Score_Ratio', 'Hist_Scoring_REG','Hist_Scoring_PP','In_PP', 'Trend', 'Weight', 'Act_Goal', 'Exp_Goal'])

    testdata['Pos_Score_Final'] = testdata['Pos_Score'] * testdata['Pos_Multiplier']
    testdata['Pos_Score_Final_Last'] = testdata['Pos_Score_Last'] * testdata['Pos_Multiplier']
    testdata['Hist_Scoring_Reg_Final'] = (testdata['Score_Ratio'] * testdata['Hist_Scoring_REG'] * testdata['Weight'] + testdata['Pos_Score_Final'] * 5) / (testdata['Weight'] + 5)
    testdata['Hist_Scoring_PP_Final'] = (testdata['Hist_Scoring_PP'] * testdata['Weight'] + testdata['Pos_Score_Final'] * 5) / (testdata['Weight'] + 5)

    x_test = testdata[['Pos_Score_Final','Pos_Score_Final_Last','Hist_Scoring']]
    y_test = testdata['Act_Goal']

    goal_scorer_model = LinearRegression()
    goal_scorer_model.fit(x_model1, y_model1)

    filename = data_directory + '/models/goal_scorer_model.sav'

    pickle.dump(goal_scorer_model, open(filename, 'wb'))

    print("COEFF", goal_scorer_model.coef_)

    test_outcome = pd.DataFrame(goal_scorer_model.predict(x_test))
    testdata['Final_Scoring'] = test_outcome

    data3 = testdata[['Final_Scoring', 'Position', 'Act_Goal']]
    evaluate_scoring_model(data3, ['CE', 'RW', 'LW', 'LD', 'RD'])

    #print(x.to_string())


def get_goal_scorer(inputs, c):

     filename = data_directory + '/models/goal_scorer_model.sav'

     goal_scorer_model = pickle.load(open(filename, 'rb'))

     inputs.columns = ('Pos_Score_Final', 'Pos_Score_Final_Last','Hist_Scoring')

     score_percent = pd.DataFrame(goal_scorer_model.predict(inputs))
     return score_percent

#update_goal_scorer(2019,"SHL",c)





