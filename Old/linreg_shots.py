#Establish connection to database

import sqlite3
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from pandas import ExcelWriter
#Model for home shots

model_shots = 'Linreg'
model_goals = 'Logreg'
verify = 0

def update_season_shots_goals(serie,seasonYear,c):

    #Model for home shots

    c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SERIE = ?",[seasonYear-1, serie])
    regdata = pd.DataFrame(c.fetchall())


    regdata.columns = ['GameID','HomeShotDelta','AwayShotDelta','Score1','Score2','Shots']

    if model_shots == 'Linreg':

        X = regdata[['HomeShotDelta','AwayShotDelta','Score1']]
        Y = regdata['Shots']

        lm = LinearRegression()
        lm.fit(X, Y)

        int1 = lm.intercept_

        c11 = lm.coef_[0]
        c12 = lm.coef_[1]
        c13 = lm.coef_[2]

    #Model for home shots random forest)

    if model_shots == 'Forest':

        X = regdata[['HomeShotDelta', 'AwayShotDelta', 'Score1','Score2']]
        Y = regdata['Shots']

    rfc = RandomForestRegressor(n_estimators=20)
    rfc.fit(X, Y)

    #Compare models

    if verify == 1:

        c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[2019, 'SHL'])
        testdata = pd.DataFrame(c.fetchall())

        testdata.columns = ['GameID', 'HomeShotDelta', 'AwayShotDelta', 'Score1', 'Score2', 'Shots']

        X_pred = testdata[['HomeShotDelta', 'AwayShotDelta', 'Score1', 'Score2']]
        Y_pred = testdata['Shots']

        rfc_pred = pd.DataFrame(rfc.predict(X_pred))

        writer = ExcelWriter('model_evaluation.xlsx')

        X_pred.to_excel(writer, 'X pred')
        Y_pred.to_excel(writer, 'Y pred')
        rfc_pred.to_excel(writer, 'RFC Pred')

        writer.save()

    #Model for away shots

    c.execute("SELECT GAMEID, AAS, AHSA, SCORE1, SCORE2, ACT_SHOTS2 FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SERIE = ?",[seasonYear-1, serie])
    regdata = pd.DataFrame(c.fetchall())


    regdata.columns = ['GameID','AwayShotDelta','HomeShotDelta','Score1','Score2','Shots']

    if model_shots == 'Linreg':

        X = regdata[['AwayShotDelta','HomeShotDelta','Score2']]
        Y = regdata['Shots']


        lm = LinearRegression()
        lm.fit(X, Y)

        int2 = lm.intercept_

        c21 = lm.coef_[0]
        c22 = lm.coef_[1]
        c23 = lm.coef_[2]

    # Model for home shots random forest)

    if model_shots == 'Forest':
        X = regdata[['HomeShotDelta', 'AwayShotDelta', 'Score1', 'Score2']]
        Y = regdata['Shots']

        rfc = RandomForestRegressor(n_estimators=20)
        rfc.fit(X, Y)

    if verify == 1:
        c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[2019, 'SHL'])
        testdata = pd.DataFrame(c.fetchall())

        testdata.columns = ['GameID', 'HomeShotDelta', 'AwayShotDelta', 'Score1', 'Score2', 'Shots']

        X_pred = testdata[['HomeShotDelta', 'AwayShotDelta', 'Score1', 'Score2']]
        Y_pred = testdata['Shots']

        rfc_pred = pd.DataFrame(rfc.predict(X_pred))

        writer = ExcelWriter('model_evaluation.xlsx')

        X_pred.to_excel(writer, 'X pred')
        Y_pred.to_excel(writer, 'Y pred')
        rfc_pred.to_excel(writer, 'RFC Pred')

        writer.save()

    c.execute("SELECT GAMEID, AHS, AHSA, AAS, AASA, SCORE1, SCORE2 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear, serie])
    upd_shots = c.fetchall()

    for i in range(0,len(upd_shots)):

        h_shots, a_shots = get_shots_goals(int1, c11, c12, c13, int2, c21, c22, c23, upd_shots[i])

        c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, INT1 = ?, INT2 = ?, C11 = ?, C12 = ?, C13 = ?, C21 =?, C22 = ?, C23 = ? WHERE GAMEID = ?",[h_shots, a_shots, int1, int2, c11, c12, c13, c21, c22, c23, upd_shots[i][0]])

    conn.commit()

    # Model for home goals (Linear regression)

    if model_goals == 'Linreg':

        c.execute("SELECT ACT_SHOTS1, ACT_GOAL1 FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SERIE = ?",[seasonYear-1, serie])
        regdata = pd.DataFrame(c.fetchall())

        if len(regdata) == 0 or regdata[0][0] == None:
            c.execute("SELECT ACT_SHOTS1, ACT_GOAL1 FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SERIE = ?",[seasonYear, serie])
            regdata = pd.DataFrame(c.fetchall())

        regdata.columns = ['Shots','Goals']

        X = regdata[['Shots']]
        Y = regdata[['Goals']]

        lm = LinearRegression()
        lm.fit(X, Y)

        int3 = lm.intercept_

        c31 = lm.coef_[0]

    # Model for home goals (Logistic regression)

    if model_goals == 'Logreg':

        c.execute("SELECT ASSH, ACSA, SCORE1, SCORE2, EXP_SHOTS1, CAST(ACT_GOAL1 AS FLOAT) / CAST(ACT_SHOTS1 AS FLOAT) FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SERIE = ?",[seasonYear-1, serie])
        regdata = pd.DataFrame(c.fetchall())

        regdata.columns = ['ASSH','ACSA','SCORE1','SCORE2','EXP_SHOTS1','EFFICIENCY']

        X = regdata[['ASSH','ACSA','SCORE1','SCORE2','EXP_SHOTS1']]
        Y = regdata[['EFFICIENCY']]

        c.execute("SELECT ASSH, ACSA, SCORE1, SCORE2, EXP_SHOTS1, CAST(ACT_GOAL1 AS FLOAT) / CAST(ACT_SHOTS1 AS FLOAT) FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear - 1, serie])
        testdata = pd.DataFrame(c.fetchall())

        testdata.columns = ['ASSH', 'ACSA', 'SCORE1', 'SCORE2', 'EXP_SHOTS1', 'EFFICIENCY']

        X_PRED = testdata[['ASSH', 'ACSA', 'SCORE1', 'SCORE2', 'EXP_SHOTS1']]
        Y_PRED = testdata[['EFFICIENCY']]

        linreg = LinearRegression()
        linreg.fit(X,Y)

        PRED = linreg.predict(X_PRED)





#update_season_shots_goals('HA',2017,c)
#update_season_shots_goals('HA',2018,c)
#update_season_shots_goals('HA',2019,c)
#update_season_shots_goals('SHL',2015,c)
#update_season_shots_goals('SHL',2016,c)
#update_season_shots_goals('SHL',2017,c)
#update_season_shots_goals('SHL',2018,c)
update_season_shots_goals('SHL',2019,c)