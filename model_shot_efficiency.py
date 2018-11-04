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
from pandas import ExcelWriter
import pickle

def update_efficiency_model_linreg(seasonYear, serie, c):

    c.execute("SELECT ACT_SHOTS1, ACT_SHOTS2, ASSH, ASSA, SCORE1-SCORE2, AGP, CAST(ACT_GOALS1 AS FLOAT)/CAST(ACT_SHOTS1 AS FLOAT), CAST(ACT_GOALS2 AS FLOAT)/CAST(ACT_SHOTS2 AS FLOAT) FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SEASON > ? AND SERIE = ?",[seasonYear - 1, seasonYear - 4, serie])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ['Shots1', 'Shots2', 'Home_Eff', 'Away_Eff', 'Score diff', 'AGP', 'Act_Eff_Home', 'Act_Eff_Away']

    #Home efficiency model

    X = regdata[['Shots1', 'Score diff', 'AGP']]
    Y = regdata[['Act_Eff_Home']]

    lm_home_efficiency = LinearRegression()
    lm_home_efficiency.fit(X, Y)

    #print(lm_home_efficiency.intercept_)
    #print(lm_home_efficiency.coef_)

    filename = data_directory + '/models/lm_shot_eff_home_' + serie + str(seasonYear) + '.sav'

    pickle.dump(lm_home_efficiency, open(filename, 'wb'))


    #Away efficiency model

    X = regdata[['Shots2', 'Score diff', 'AGP']]
    Y = regdata[['Act_Eff_Away']]

    lm_away_efficiency = LinearRegression()
    lm_away_efficiency.fit(X, Y)

    #print(lm_away_efficiency.intercept_)
    #print(lm_away_efficiency.coef_)

    filename = data_directory + '/models/lm_shot_eff_away_' + serie + str(seasonYear) + '.sav'

    pickle.dump(lm_away_efficiency, open(filename, 'wb'))

    # Update model_shot_table with exp_shots

    c.execute("SELECT EXP_SHOTS1, EXP_SHOTS2, SCORE1-SCORE2, AGP, GAMEID FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear, serie])
    upd = c.fetchall()

    for i in range(0, len(upd)):
        exp_goals_home = lm_home_efficiency.predict([[upd[i][0], upd[i][2], upd[i][3]]])[0][0]*upd[i][0]
        exp_goals_away = lm_away_efficiency.predict([[upd[i][1], upd[i][2], upd[i][3]]])[0][0]*upd[i][1]

        c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_GOALS1 = ?, EXP_GOALS2 = ? WHERE GAMEID = ?", [exp_goals_home, exp_goals_away, upd[i][4]])

    conn.commit()


def get_efficiency_model_linreg(seasonYear, inputs, gameid, serie, c):

    filename = data_directory + '/models/lm_shot_eff_home_' + serie + str(seasonYear) + '.sav'

    lm_home_efficiency = pickle.load(open(filename, 'rb'))

    #print(lm_home_efficiency.intercept_)
    #print(lm_home_efficiency.coef_)

    int1 = lm_home_efficiency.intercept_
    c11 = lm_home_efficiency.coef_[0][0]
    c12 = lm_home_efficiency.coef_[0][1]
    c13 = lm_home_efficiency.coef_[0][2]

    h_goals = (int1 + c11 * inputs[0] + c12 * inputs[2] + c13 * inputs[3]) * inputs[0]

    filename = data_directory + '/models/lm_shot_eff_away_' + serie + str(seasonYear) + '.sav'

    lm_away_efficiency = pickle.load(open(filename, 'rb'))

    int2 = lm_away_efficiency.intercept_
    c21 = lm_away_efficiency.coef_[0][0]
    c22 = lm_away_efficiency.coef_[0][1]
    c23 = lm_away_efficiency.coef_[0][2]

    a_goals = (int2 + c21 * inputs[1] + c22 * inputs[2] + c23 * inputs[3]) * inputs[1]

    c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_GOALS1 = ?, EXP_GOALS2 = ? WHERE gameid = ?",[h_goals[0], a_goals[0], gameid])

    conn.commit()

    return h_goals[0], a_goals[0]




#update_efficiency_model_linreg(2019,'SHL',c)
#update_efficiency_model_linreg(2018,'SHL',c)
#update_efficiency_model_linreg(2017,'SHL',c)
#update_efficiency_model_linreg(2016,'SHL',c)


update_efficiency_model_linreg(2019,'SHL',c)
update_efficiency_model_linreg(2018,'SHL',c)

#update_efficiency_model_linreg(2018,'SHL',c)
#update_efficiency_model_linreg(2017,'SHL',c)
#update_efficiency_model_linreg(2016,'SHL',c)

#update_efficiency_model_linreg(2019, 'HA', c)
#update_efficiency_model_linreg(2018, 'HA', c)

