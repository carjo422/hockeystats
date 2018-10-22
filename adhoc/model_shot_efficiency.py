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

def update_efficiency_model_linreg(serie,seasonYear,c):

    c.execute("SELECT ACT_SHOTS1, ASSH, ACSH, ASSA, ACSA, SCORE1, SCORE2, ACT_GOAL1/ACT, ACT_GOAL2/ACT_SHOTS2 FROM EXP_SHOTS_TABLE WHERE SEASON <= ? AND SERIE = ?",[seasonYear - 1, serie])
    regdata = pd.DataFrame(c.fetchall())

    regdata.columns = ['Shots', 'Home_Eff_Off', 'Home_Eff_Def', 'Away_Eff_Off', 'Away_Eff_Def', 'Score1', 'Score2', 'Act_Eff_Home', 'Act_Eff_Away']

    X = regdata[['Shots', 'Home_Eff_Off', 'Away_Eff_Def']]
    Y = regdata[['Goals']]

    lm = LinearRegression()
    lm.fit(X, Y)

    int3 = lm.intercept_

    c31 = lm.coef_[0]

