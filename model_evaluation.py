import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
import scipy.stats
from pandas import ExcelWriter

exp_matrix = pd.DataFrame(np.zeros((11, 11)))
act_matrix = pd.DataFrame(np.zeros((11, 11)))

def exp_act_results(year_vector,serie_vector):

    for i in range(0,len(year_vector)):
        for j in range(0,len(serie_vector)):

            c.execute("SELECT EXP_GOAL1, EXP_GOAL2, ACT_GOAL1, ACT_GOAL2 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[year_vector[i], serie_vector[j]])
            ev_matrix = c.fetchall()

            for k in range(0,len(ev_matrix)):

                if ev_matrix[k][2] + ev_matrix[k][3] < 10:
                    act_matrix[ev_matrix[k][2]][ev_matrix[k][3]] += 1

                for m1 in range(0,10):
                    for m2 in range(0,10):

                        if m1+m2 < 10:
                            exp_matrix[m1][m2] += scipy.stats.distributions.poisson.pmf(m1,ev_matrix[k][0]) * scipy.stats.distributions.poisson.pmf(m2, ev_matrix[k][1])



def exp_act_nGoals(year_vector, serie_vector):

    act_goals = 0
    exp_goals = 0

    for i in range(0, len(year_vector)):
        for j in range(0, len(serie_vector)):

            c.execute("SELECT SEASON, SERIE, SUM(EXP_GOAL1), SUM(EXP_GOAL2), SUM(ACT_GOAL1), SUM(ACT_GOAL2) FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ? GROUP BY SEASON, SERIE ORDER BY SERIE, SEASON",[year_vector[i], serie_vector[j]])
            print(c.fetchall())


exp_act_results([2016,2017,2018,2019],['SHL'])
exp_act_nGoals([2016,2017,2018,2019],['SHL'])



print(act_matrix)
print(exp_matrix)

writer = ExcelWriter('model_evaluation.xlsx')
act_matrix.to_excel(writer,'Act_matrix')
exp_matrix.to_excel(writer,'Exp_matrix')
writer.save()