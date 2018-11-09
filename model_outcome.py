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


def update_outcome_model1(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, ACT_GOALS1-ACT_GOALS2 FROM GOALS_FOREST_TABLE_1 WHERE GAMEDATE > ? AND SEASONID < ?",['2015-10-15', seasonYear])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('OSH', 'DSH','OSA', 'DSA', 'ACT_DIFF')


    x = regdata[regdata.columns[0:4]]
    y = regdata[regdata.columns[4]]

    # Test data

    c.execute("SELECT HOMETEAM, AWAYTEAM, OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, ACT_GOALS1-ACT_GOALS2 FROM GOALS_FOREST_TABLE_1 WHERE GAMEDATE > ? AND SEASONID = ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    test_data = pd.DataFrame(c.fetchall())

    test_data.columns = ('HT','AT','OSH', 'DSH', 'OSA', 'DSA', 'ACT_DIFF')

    x_test = test_data[test_data.columns[2:6]]
    y_test = test_data[test_data.columns[6]]

    outcome_model1 = LinearRegression()
    outcome_model1.fit(x, y)

    #print(outcome_model1.coef_, outcome_model1.intercept_)

    filename = data_directory + '/models/outcome_model1_' + serie + str(seasonYear) + '.sav'

    pickle.dump(outcome_model1, open(filename, 'wb'))

    test_outcome = pd.DataFrame(outcome_model1.predict(x_test))
    test_data['EXP_DIFF'] = test_outcome

    #print(test_data)

    print("Mean squared error Linreg Diff: ", mean_squared_error(y_test, test_outcome))



def update_outcome_model2(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT COMB_SCORE_HOME, COMB_SCORE_AWAY, ACT_GOALS1-ACT_GOALS2 FROM GOALS_FOREST_TABLE_2 WHERE GAMEDATE > ? AND SEASONID < ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('CSH','CSA','ACT_DIFF')

    x = regdata[regdata.columns[0:2]]
    y1 = regdata[regdata.columns[2]]


    outcome_model2 = LinearRegression()
    outcome_model2.fit(x, y1)

    #print(outcome_model2.coef_, outcome_model2.intercept_)

    filename = data_directory + '/models/outcome_model2_' + serie + str(seasonYear) + '.sav'

    pickle.dump(outcome_model2, open(filename, 'wb'))

    #test_outcome1 = pd.DataFrame(forest_outcome1.predict(x_test))


def get_outcome_model1(serie, seasonYear, inputs, c):

    filename1 = data_directory + '/models/outcome_model1_' + serie + str(seasonYear) + '.sav'

    outcome_model1 = pickle.load(open(filename1, 'rb'))

    inputs.columns = ['OSH', 'DSH', 'OSA', 'DSA']

    diff = pd.DataFrame(outcome_model1.predict(inputs))

    return diff[0][0]




def get_outcome_model2(serie, seasonYear, inputs, c):

    filename1 = data_directory + '/models/outcome_model2_' + serie + str(seasonYear) + '.sav'

    outcome_model2 = pickle.load(open(filename1, 'rb'))

    inputs.columns = ['CSH','CSA']

    diff = pd.DataFrame(outcome_model2.predict(inputs))

    return diff[0][0]


#update_model1_data(serie, c, conn)
update_outcome_model1(2019,"SHL",c)
#update_outcome_model1(2019,"HA",c)

#update_model2_data(serie, seasonYear, c, conn)
update_outcome_model2(2019,"SHL",c)
#update_outcome_model2(2019,"HA",c)

#update_forest_data('HA')



