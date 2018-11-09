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
from sklearn.metrics import mean_squared_error
import pickle


def update_nGoals_model(seasonYear,c):

    # Train data

    c.execute("SELECT ABS(SCORE1/SCORE2-1), OFF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_HOME, DEF_SCORE_AWAY, ACT_GOALS1+ACT_GOALS2 FROM GOALS_FOREST_TABLE_1 WHERE SEASONID < ?",[seasonYear])
    regdata = pd.DataFrame(c.fetchall())

    c.execute("SELECT ABS(SCORE1/SCORE2-1), OFF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_HOME, DEF_SCORE_AWAY, ACT_GOALS1+ACT_GOALS2 FROM GOALS_FOREST_TABLE_1 WHERE SEASONID = ?",[seasonYear])
    testdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('SCORE_RATIO', 'OSH', 'OSA', 'DSH', 'DSA','SUM_GOALS')
    testdata.columns = ('SCORE_RATIO', 'OSH', 'OSA', 'DSH', 'DSA', 'SUM_GOALS')

    x = regdata[regdata.columns[0:5]]
    y = regdata[regdata.columns[5]]

    x_test = testdata[testdata.columns[0:5]]
    y_test = testdata[testdata.columns[5]]

    nGoals_model = LinearRegression()
    nGoals_model.fit(x, y)

    #print(nGoals_model.coef_, nGoals_model.intercept_)

    filename = data_directory + '/models/nGoals_model_' + str(seasonYear) + '.sav'

    pickle.dump(nGoals_model, open(filename, 'wb'))

    y_pred = nGoals_model.predict(x_test)
    print("Mean square error:", mean_squared_error(y_test, y_pred))
    testdata['Pred'] = y_pred

    print(testdata)

    print(testdata['Pred'].sum(), testdata['SUM_GOALS'].sum())

def get_nGoals_model(seasonYear, inputs, c):
    filename = data_directory + '/models/nGoals_model_' + str(seasonYear) + '.sav'

    nGoals_model = pickle.load(open(filename, 'rb'))
    inputs.columns = ('SCORE_RATIO', 'OSH', 'OSA', 'DSH', 'DSA')

    sum = pd.DataFrame(nGoals_model.predict(inputs))

    return sum[0][0]

#update_nGoals_model(2019,c)