#Establish connection to database

import sqlite3
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from create_pre_match_tables import get_shots_goals

#Model for home shots

def update_season_shots_goals(serie,seasonYear,c):

    c.execute("SELECT GAMEID, AHS, AASA, SCORE1, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear-1, serie])
    regdata = pd.DataFrame(c.fetchall())
    regdata.columns = ['GameID','HomeShotDelta','AwayShotDelta','Score','Shots']

    X = regdata[['HomeShotDelta','AwayShotDelta','Score']]
    Y = regdata['Shots']

    X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size = 0.2, random_state=101)

    lm = LinearRegression()
    lm.fit(X_train, Y_train)

    int1 = lm.intercept_

    c11 = lm.coef_[0]
    c12 = lm.coef_[1]
    c13 = lm.coef_[2]

    #Model for away shots

    c.execute("SELECT GAMEID, AAS, AHSA, SCORE2, ACT_SHOTS2 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear-1, serie])
    regdata = pd.DataFrame(c.fetchall())
    regdata.columns = ['GameID','AwayShotDelta','HomeShotDelta','Score','Shots']

    X = regdata[['AwayShotDelta','HomeShotDelta','Score']]
    Y = regdata['Shots']

    X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size = 0.2, random_state=101)

    lm = LinearRegression()
    lm.fit(X_train, Y_train)

    int2 = lm.intercept_

    c21 = lm.coef_[0]
    c22 = lm.coef_[1]
    c23 = lm.coef_[2]



    c.execute("SELECT GAMEID, AHS, AHSA, ASSH, ACSH, AAS, AASA, ASSA, ACSA, SCORE1, SCORE2 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear, serie])
    upd_shots = c.fetchall()

    for i in range(0,len(upd_shots)):

        h_shots, a_shots, h_goals, a_goals = get_shots_goals(int1, c11, c12, c13, int2, c21, c22, c23, upd_shots[i])

        c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, EXP_GOAL1 = ?, EXP_GOAL2 = ?, INT1 = ?, INT2 = ?, C11 = ?, C12 = ?, C13 = ?, C21 =?, C22 = ?, C23 = ? WHERE GAMEID = ?",[h_shots, a_shots, h_goals, a_goals, int1, int2, c11, c12, c13, c21, c22, c23, upd_shots[i][0]])

    conn.commit()

update_season_shots_goals('SHL',2019,c)