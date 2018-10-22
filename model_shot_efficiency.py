#Establish connection to database

import os

if os.path.exists('/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/'):
    data_directory = '/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/'
else:
    data_directory = '/Users/carljonsson/Python/hockeystats/hockeystats.db'

import sqlite3
conn = sqlite3.connect(data_directory + '/hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from pandas import ExcelWriter
import pickle

def update_efficiency_model_linreg(seasonYear,c):

    c.execute("SELECT AVG(ASSH), AVG(ASSA) FROM EXP_SHOTS_TABLE WHERE SEASON <= ?",[seasonYear - 1])
    avgs = c.fetchall()

    c.execute("SELECT ACT_SHOTS1, ACT_SHOTS2, ASSH+ACSA - ?, ASSA+ACSH - ?, SCORE1, SCORE2, CAST(ACT_GOALS1 AS FLOAT)/CAST(ACT_SHOTS1 AS FLOAT), CAST(ACT_GOALS2 AS FLOAT)/CAST(ACT_SHOTS2 AS FLOAT) FROM EXP_SHOTS_TABLE WHERE SEASON <= ?",[avgs[0][0]*2, avgs[0][1]*2, seasonYear - 1])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ['Shots1', 'Shots2', 'Home_Eff_Delta', 'Away_Eff_Delta', 'Score1', 'Score2', 'Act_Eff_Home', 'Act_Eff_Away']

    #Home efficiency model

    X = regdata[['Shots1', 'Score1', 'Score2']]
    Y = regdata[['Act_Eff_Home']]

    lm_home_efficiency = LinearRegression()
    lm_home_efficiency.fit(X, Y)

    filename = data_directory + '/models/lm_shot_eff_home_' + str(seasonYear) + '.sav'

    pickle.dump(lm_home_efficiency, open(filename, 'wb'))


    #Away efficiency model

    X = regdata[['Shots2', 'Score2', 'Score1']]
    Y = regdata[['Act_Eff_Away']]

    lm_away_efficiency = LinearRegression()
    lm_away_efficiency.fit(X, Y)

    filename = data_directory + '/models/lm_shot_eff_away_' + str(seasonYear) + '.sav'

    pickle.dump(lm_away_efficiency, open(filename, 'wb'))

    # Update model_shot_table with exp_shots

    c.execute("SELECT EXP_SHOTS1, EXP_SHOTS2, SCORE1, SCORE2, GAMEID FROM EXP_SHOTS_TABLE WHERE SEASON = ?",[seasonYear])
    upd = c.fetchall()

    for i in range(0, len(upd)):
        exp_goals_home = lm_home_efficiency.predict([[upd[i][0], upd[i][2], upd[i][3]]])[0][0]
        exp_goals_away = lm_away_efficiency.predict([[upd[i][1], upd[i][3], upd[i][2]]])[0][0]

        c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_GOALS1 = ?, EXP_GOALS2 = ?, SHOT_MODEL = ? WHERE GAMEID = ?", [exp_goals_home, exp_goals_away, "LINREG", upd[i][4]])

    conn.commit()


def get_efficiency_model_linreg(seasonYear, inputs, gameid,c):

    filename = data_directory + '/models/lm_shot_eff_home_' + str(seasonYear) + '.sav'

    lm_home_efficiency = pickle.load(open(filename, 'rb'))

    int1 = lm_home_efficiency.intercept_
    c11 = lm_home_efficiency.coef_[0][0]
    c12 = lm_home_efficiency.coef_[0][1]
    c13 = lm_home_efficiency.coef_[0][2]

    h_goals = (int1 + c11 * inputs[0] + c12 * inputs[2] + c13 * inputs[3]) * inputs[0]

    filename = data_directory + '/models/lm_shot_eff_away_' + str(seasonYear) + '.sav'

    lm_away_efficiency = pickle.load(open(filename, 'rb'))

    int2 = lm_away_efficiency.intercept_
    c21 = lm_away_efficiency.coef_[0][0]
    c22 = lm_away_efficiency.coef_[0][1]
    c23 = lm_away_efficiency.coef_[0][2]

    a_goals = (int2 + c21 * inputs[1] + c22 * inputs[3] + c23 * inputs[2]) * inputs[1]

    c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_GOALS1 = ?, EXP_GOALS2 = ?, GOAL_MODEL = ? WHERE gameid = ?",[h_goals, a_goals, "LINREG", gameid])

    conn.commit()

    return h_goals[0], a_goals[0]


update_efficiency_model_linreg(2016,c)