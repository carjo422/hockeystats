#Establish connection to database

import sqlite3
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from pandas import ExcelWriter
import pickle

def update_shots_model_linreg(serie,seasonYear,c):

    #Model for home shots

    c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SERIE = ? AND SEASON < ?",[serie,seasonYear])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ['GameID','HomeShotDelta','AwayShotDelta','Score1','Score2','Shots']

    X = regdata[['HomeShotDelta','AwayShotDelta','Score1']]
    Y = regdata['Shots']

    lm_home_shots = LinearRegression()
    lm_home_shots.fit(X, Y)

    filename = '/Users/carljonsson/Python/hockeystats/models/lm_home_shots_' + str(seasonYear) + '.sav'
    pickle.dump(lm_home_shots, open(filename, 'wb'))

    # Model for away shots

    c.execute("SELECT GAMEID, AAS, AHSA, SCORE1, SCORE2, ACT_SHOTS2 FROM EXP_SHOTS_TABLE WHERE SERIE = ? AND SEASON < ?",[serie, seasonYear])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ['GameID', 'AwayShotDelta', 'HomeShotDelta', 'Score1', 'Score2', 'Shots']

    X = regdata[['AwayShotDelta', 'HomeShotDelta', 'Score2']]
    Y = regdata['Shots']

    lm_away_shots = LinearRegression()
    lm_away_shots.fit(X, Y)

    filename = '/Users/carljonsson/Python/hockeystats/models/lm_away_shots_' + str(seasonYear) + '.sav'
    pickle.dump(lm_away_shots, open(filename, 'wb'))

    #Update model_shot_table with exp_shots

    c.execute("SELECT AHS, AASA, AAS, AHSA, SCORE1, SCORE2, GAMEID FROM EXP_SHOTS_TABLE WHERE SERIE = ? AND SEASON = ?",[serie, seasonYear])
    upd = c.fetchall()

    for i in range(0,len(upd)):
        exp_shots_home = lm_home_shots.predict([[upd[i][0],upd[i][1],upd[i][4]]])[0]
        exp_shots_away = lm_away_shots.predict([[upd[i][2],upd[i][3],upd[i][5]]])[0]

        c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, SHOT_MODEL = ? WHERE GAMEID = ?", [exp_shots_home, exp_shots_away, "LINREG", upd[i][6]])

    conn.commit()


def update_shots_model_forest(serie,seasonYear,c):

    #Model for home shots random forest)

    c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SERIE = ? AND SEASON < ?",[serie, seasonYear])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ['GameID', 'AwayShotDelta', 'HomeShotDelta', 'Score1', 'Score2', 'Shots']

    X = regdata[['HomeShotDelta', 'AwayShotDelta', 'Score1','Score2']]
    Y = regdata['Shots']

    forest_home_shots = RandomForestRegressor(n_estimators=500)
    forest_home_shots.fit(X, Y)

    filename = '/Users/carljonsson/Python/hockeystats/models/forest_home_shots_' + str(seasonYear) + '.sav'
    pickle.dump(forest_home_shots, open(filename, 'wb'))

    # Model for away shots random forest)

    X = regdata[['AwayShotDelta', 'HomeShotDelta', 'Score2', 'Score1']]
    Y = regdata['Shots']

    forest_away_shots = RandomForestRegressor(n_estimators=500)
    forest_away_shots.fit(X, Y)

    filename = '/Users/carljonsson/Python/hockeystats/models/forest_away_shots_' + str(seasonYear) + '.sav'
    pickle.dump(forest_away_shots, open(filename, 'wb'))





def get_shots_goals_linreg(seasonYear, shots, gameid):

    filename = '/Users/carljonsson/Python/hockeystats/models/lm_home_shots_' + str(seasonYear) + '.sav'

    lm_home_shots = pickle.load(open(filename, 'rb'))

    int1 = lm_home_shots.intercept_
    c11 = lm_home_shots.coef_[0]
    c12 = lm_home_shots.coef_[1]
    c13 = lm_home_shots.coef_[2]

    h_shots = int1 + c11 * shots[0] + c12 * shots[3] + c13 * shots[4]

    filename = '/Users/carljonsson/Python/hockeystats/models/lm_away_shots_' + str(seasonYear) + '.sav'

    lm_away_shots = pickle.load(open(filename, 'rb'))

    int2 = lm_away_shots.intercept_
    c21 = lm_away_shots.coef_[0]
    c22 = lm_away_shots.coef_[1]
    c23 = lm_away_shots.coef_[2]

    a_shots = int2 + c21 * shots[1] + c22 * shots[2] + c23 * shots[5]

    c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, SHOT_MODEL = ? WHERE gameid = ?",[h_shots, a_shots, "LINREG", gameid])

    conn.commit()

    return h_shots, a_shots

def get_shots_goals_forest(seasonYear, shots, gameid):

    filename = '/Users/carljonsson/Python/hockeystats/models/forest_home_shots_' + str(seasonYear) + '.sav'

    forest_home_shots = pickle.load(open(filename, 'rb'))

    h_shots = forest_home_shots.predict([[shots[0], shots[1], shots[4], shots[5]]])

    filename = '/Users/carljonsson/Python/hockeystats/models/forest_away_shots_' + str(seasonYear) + '.sav'

    forest_away_shots = pickle.load(open(filename, 'rb'))

    a_shots = forest_away_shots.predict([[shots[1], shots[0], shots[5], shots[4]]])

    c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, SHOT_MODEL = ? WHERE gameid = ?",[h_shots, a_shots, "FOREST", gameid])

    conn.commit()

    return h_shots, a_shots


update_shots_model_linreg('HA',2018,c)
#update_shots_model_forest('SHL',2019,c)
#get_shots_goals_linreg(2019, [3,-3,-3,-2,6,4], "")
#get_shots_goals_forest(2019, [3,-3,-3,-2,6,4], "")