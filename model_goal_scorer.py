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
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from pandas import ExcelWriter
import pickle
from create_pre_match_tables import update_model1_data
from create_pre_match_tables import update_model2_data


def update_goal_scorer(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT BASE_SCORING, HIST_SCORING, IN_PP, ACT_GOAL FROM EXP_GOAL_SCORER")
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('BS', 'HS', 'INPP', 'ACT_GOAL')


    x = regdata[regdata.columns[0:3]]
    y = regdata[regdata.columns[3]]

    # Test data

    c.execute("SELECT BASE_SCORING, HIST_SCORING, IN_PP, ACT_GOAL FROM EXP_GOAL_SCORER")
    test_data = pd.DataFrame(c.fetchall())

    test_data.columns = ('BS', 'HS', 'INPP', 'ACT_GOAL')

    x_test = test_data[test_data.columns[0:3]]
    y_test = test_data[test_data.columns[3]]

    goal_scorer_model = LinearRegression()
    goal_scorer_model.fit(x, y)

    #print(outcome_model1.coef_, outcome_model1.intercept_)

    filename = data_directory + '/models/goal_scorer_model.sav'

    pickle.dump(goal_scorer_model, open(filename, 'wb'))

    test_outcome = pd.DataFrame(goal_scorer_model.predict(x_test))
    test_data['EXP_DIFF'] = test_outcome

    #print(test_data)

    print(goal_scorer_model.coef_)
    print(goal_scorer_model.intercept_)

    print("Mean squared error Linreg Diff: ", mean_squared_error(y_test, test_outcome))


def get_outcome_model1(serie, seasonYear, inputs, c):

    filename1 = data_directory + '/models/goal_scorer_model.sav'

    goal_scorer_model = pickle.load(open(filename1, 'rb'))

    inputs.columns = ('BS', 'HS', 'INPP')

    diff = pd.DataFrame(goal_scorer_model.predict(inputs))

    return diff[0][0]

update_goal_scorer(2019,"SHL",c)





