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
from sklearn.ensemble import RandomForestRegressor
from pandas import ExcelWriter
import pickle
from create_pre_match_tables import update_forest_data_1
#from create_pre_match_tables import update_forest_data_2


def update_shots_model_forest_1(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT SCORE1, SCORE2, OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, ACT_GOALS1, ACT_GOALS2, OUTCOME45 FROM GOALS_FOREST_TABLE_1 WHERE GAMEDATE > ? AND SEASONID < ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('SC1','SC2','OSH', 'DSH','OSA', 'DSA', 'ACT_GOALS1', 'ACT_GOALS2', 'OUT45')

    regdata['ACT_GOALS1'].apply(int)
    regdata['ACT_GOALS2'].apply(int)
    regdata['OUT45'].apply(int)

    x = regdata[regdata.columns[0:6]]
    y1 = regdata[regdata.columns[6]]
    y2 = regdata[regdata.columns[7]]
    y45 = regdata[regdata.columns[8]]

    # Test data

    c.execute("SELECT HOMETEAM, AWAYTEAM, SCORE1, SCORE2, OFF_SCORE_HOME, DEF_SCORE_HOME, OFF_SCORE_AWAY, DEF_SCORE_AWAY, ACT_GOALS1, ACT_GOALS2, OUTCOME45 FROM GOALS_FOREST_TABLE_1 WHERE GAMEDATE > ? AND SEASONID = ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    test_data = pd.DataFrame(c.fetchall())

    test_data.columns = ('HT','AT','SC1','SC2','OSH', 'DSH', 'OSA', 'DSA', 'ACT_GOALS1', 'ACT_GOALS2', 'OUT45')

    regdata['ACT_GOALS1'].apply(int)
    regdata['ACT_GOALS2'].apply(int)
    test_data['OUT45'].apply(int)

    x_test = test_data[test_data.columns[2:8]]
    y_test1 = test_data[test_data.columns[8]]
    y_test2 = test_data[test_data.columns[9]]
    y_test45 = test_data[test_data.columns[10]]



    forest_outcome1 = RandomForestRegressor(n_estimators=1000, max_depth=2, min_samples_split=4)
    forest_outcome1.fit(x, y1)

    filename = data_directory + '/models/forest_outcome1_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome1, open(filename, 'wb'))

    test_outcome1 = pd.DataFrame(forest_outcome1.predict(x_test))



    forest_outcome2 = RandomForestRegressor(n_estimators=1000, max_depth=2, min_samples_split=4)
    forest_outcome2.fit(x, y2)

    filename = data_directory + '/models/forest_outcome2_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome2, open(filename, 'wb'))

    test_outcome2 = pd.DataFrame(forest_outcome2.predict(x_test))



    forest_outcome45 = RandomForestClassifier(n_estimators=1000, max_depth=2, min_samples_split=4)
    forest_outcome45.fit(x, y45)

    filename = data_directory + '/models/forest_outcome45_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome45, open(filename, 'wb'))

    test_outcome45 = pd.DataFrame(forest_outcome45.predict_proba(x_test))


def update_shots_model_forest_2(seasonYear,serie,c):

    #Model for home shots random forest)

    # Train data

    c.execute("SELECT COMB_SCORE_HOME, COMB_SCORE_AWAY, ACT_GOALS1, ACT_GOALS2, OUTCOME45 FROM GOALS_FOREST_TABLE_2 WHERE GAMEDATE > ? AND SEASONID < ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ('CSH','CSA','ACT_GOALS1', 'ACT_GOALS2', 'OUT45')

    regdata['ACT_GOALS1'].apply(int)
    regdata['ACT_GOALS2'].apply(int)
    regdata['OUT45'].apply(int)

    x = regdata[regdata.columns[0:2]]
    y1 = regdata[regdata.columns[2]]
    y2 = regdata[regdata.columns[3]]
    y45 = regdata[regdata.columns[4]]

    # Test data

    #c.execute("SELECT COMB_SCORE_HOME, COMB_SCORE_AWAY, ACT_GOALS1, ACT_GOALS2, OUTCOME45 FROM GOALS_FOREST_TABLE_2 WHERE GAMEDATE > ? AND SEASONID = ? AND SERIE = ?",['2015-10-15', seasonYear, serie])
    #test_data = pd.DataFrame(c.fetchall())

    #test_data.columns = ('CSH','CSA','ACT_GOALS1', 'ACT_GOALS2', 'OUT45')

    #regdata['ACT_GOALS1'].apply(int)
    #regdata['ACT_GOALS2'].apply(int)
    #test_data['OUT45'].apply(int)

    #x_test = regdata[regdata.columns[0:1]]
    #y_test1 = regdata[regdata.columns[2]]
    #y_test2 = regdata[regdata.columns[3]]
    #y_test45 = regdata[regdata.columns[4]]


    forest_outcome1 = RandomForestRegressor(n_estimators=1000, max_depth=2, min_samples_split=4)
    forest_outcome1.fit(x, y1)

    filename = data_directory + '/models/forest2_outcome1_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome1, open(filename, 'wb'))

    #test_outcome1 = pd.DataFrame(forest_outcome1.predict(x_test))



    forest_outcome2 = RandomForestRegressor(n_estimators=1000, max_depth=2, min_samples_split=4)
    forest_outcome2.fit(x, y2)

    filename = data_directory + '/models/forest2_outcome2_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome2, open(filename, 'wb'))

    #test_outcome2 = pd.DataFrame(forest_outcome2.predict(x_test))



    forest_outcome45 = RandomForestClassifier(n_estimators=1000, max_depth=2, min_samples_split=4)
    forest_outcome45.fit(x, y45)

    filename = data_directory + '/models/forest2_outcome45_' + serie + str(seasonYear) + '.sav'

    pickle.dump(forest_outcome45, open(filename, 'wb'))

    #test_outcome45 = pd.DataFrame(forest_outcome45.predict_proba(x_test))


def get_outcome_model_forest_1(serie, seasonYear, inputs, c):

    filename1 = data_directory + '/models/forest_outcome1_' + serie + str(seasonYear) + '.sav'
    filename2 = data_directory + '/models/forest_outcome2_' + serie + str(seasonYear) + '.sav'
    filename3 = data_directory + '/models/forest_outcome45_' + serie + str(seasonYear) + '.sav'

    forest_outcome1 = pickle.load(open(filename1, 'rb'))
    forest_outcome2 = pickle.load(open(filename2, 'rb'))
    forest_outcome45 = pickle.load(open(filename3, 'rb'))

    inputs.columns = ['SC1','SC2', 'OSH', 'DSH', 'OSA', 'DSA']

    g1 = pd.DataFrame(forest_outcome1.predict(inputs))
    g2 = pd.DataFrame(forest_outcome2.predict(inputs))
    odds45 = pd.DataFrame(forest_outcome45.predict_proba(inputs))

    return g1[0][0], g2[0][0], odds45





def get_outcome_model_forest_2(serie, seasonYear, inputs, c):

    filename1 = data_directory + '/models/forest2_outcome1_' + serie + str(seasonYear) + '.sav'
    filename2 = data_directory + '/models/forest2_outcome2_' + serie + str(seasonYear) + '.sav'
    filename3 = data_directory + '/models/forest2_outcome45_' + serie + str(seasonYear) + '.sav'

    forest_outcome1 = pickle.load(open(filename1, 'rb'))
    forest_outcome2 = pickle.load(open(filename2, 'rb'))
    forest_outcome45 = pickle.load(open(filename3, 'rb'))

    inputs.columns = ['CSH','CSA']

    g1 = pd.DataFrame(forest_outcome1.predict(inputs))
    g2 = pd.DataFrame(forest_outcome2.predict(inputs))
    odds45 = pd.DataFrame(forest_outcome45.predict_proba(inputs))

    return g1[0][0], g2[0][0], odds45


#update_forest_data_1('SHL', c, conn)
update_shots_model_forest_1(2019,"SHL",c)

#update_forest_data2('SHL')
update_shots_model_forest_2(2019,"SHL",c)

#update_forest_data('HA')
#update_shots_model_forest(2019,"HA",c)
