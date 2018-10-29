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
from sklearn.ensemble import RandomForestClassifier
from pandas import ExcelWriter
import pickle
from create_pre_match_tables import update_forest_data


def update_shots_model_forest(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT SCORE1, SCORE2, OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, OUTCOME1X2, OUTCOME45 FROM ANN_TABLE WHERE GAMEDATE > ? AND SEASONID < ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('OSH', 'DSH','SC1','SC2','OSA', 'DSA', 'OUT1X2', 'OUT45')

    regdata['OUT1X2'].apply(int)
    regdata['OUT45'].apply(int)

    x = regdata[regdata.columns[2:6]]
    y = regdata[regdata.columns[6]]

    # Test data

    c.execute("SELECT HOMETEAM, AWAYTEAM, SCORE1, SCORE2, OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, OUTCOME1X2, OUTCOME45 FROM ANN_TABLE WHERE GAMEDATE > ? AND SEASONID = ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    test_data = pd.DataFrame(c.fetchall())

    test_data.columns = ('HT','AT','SC1','SC2','OSH', 'DSH', 'OSA', 'DSA', 'OUT1X2', 'OUT45')

    test_data['OUT1X2'].apply(int)
    test_data['OUT45'].apply(int)

    x_test = test_data[test_data.columns[4:8]]
    y_test = test_data[test_data.columns[8]]



    forest_outcome = RandomForestClassifier(n_estimators=1000, max_depth=2, min_samples_split=5)
    forest_outcome.fit(x, y)

    filename = data_directory + '/models/forest_outcome_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome, open(filename, 'wb'))

    test_outcome = pd.DataFrame(forest_outcome.predict_proba(x_test))

    test_data['p1'] = test_outcome[0]
    test_data['pX'] = test_outcome[1]
    test_data['p2'] = test_outcome[2]

    print(test_data)


def get_outcome_model_forest(serie, seasonYear, c):

    filename = data_directory + '/models/forest_outcome_' + serie + str(seasonYear) + '.sav'

    forest_outcome = pickle.load(open(filename, 'rb'))

    inputs = get_inputs_forest_model()

    inputs.columns = ['OSH', 'DSH', 'OSA', 'DSA']


    odds1X2 = pd.DataFrame(forest_outcome.predict_proba(inputs))


#update_forest_data()
#update_shots_model_forest(2019,"SHL",c)
