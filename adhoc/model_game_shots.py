#Establish connection to database

import sqlite3
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from pandas import ExcelWriter
#Model for home shots

model_shots = 'Linreg'
verify = 0

def update_shots_model(serie,seasonYear,c):

    #Model for home shots

    c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE AND SERIE = ? AND SEASON < ?",[serie,seasonYear])
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

        c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear, serie])
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

    c.execute("SELECT GAMEID, AAS, AHSA, SCORE1, SCORE2, ACT_SHOTS2 FROM EXP_SHOTS_TABLE WHERE AND SERIE = ? AND SEASON < ?",[serie,seasonYear])
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

    # Model for away shots random forest)

    if model_shots == 'Forest':
        X = regdata[['AwayShotDelta', 'HomeShotDelta', 'Score2', 'Score1']]
        Y = regdata['Shots']

        rfc = RandomForestRegressor(n_estimators=20)
        rfc.fit(X, Y)


    #Compare models vs each other

    if verify == 1:
        c.execute("SELECT GAMEID, AHS, AASA, SCORE1, SCORE2, ACT_SHOTS1 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear, serie])
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

    #Update data

    c.execute("SELECT GAMEID, AHS, AHSA, AAS, AASA, SCORE1, SCORE2 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[seasonYear, serie])
    upd_shots = c.fetchall()

    for i in range(0,len(upd_shots)):

        h_shots, a_shots = get_shots_goals_linreg(int1, c11, c12, c13, int2, c21, c22, c23, upd_shots[i])

        c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, INT1 = ?, INT2 = ?, C11 = ?, C12 = ?, C13 = ?, C21 =?, C22 = ?, C23 = ? WHERE GAMEID = ?",[h_shots, a_shots, int1, int2, c11, c12, c13, c21, c22, c23, upd_shots[i][0]])

    conn.commit()


def get_shots_goals_linreg(int1, c11, c12, c13, int2, c21, c22, c23, shots):
    h_shots = int1 + c11 * shots[1] + c12 * shots[4] + c13 * shots[5]
    a_shots = int2 + c21 * shots[2] + c22 * shots[3] + c23 * shots[6]

    return h_shots, a_shots


update_shots_model('SHL',2019,c)