import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

import pandas as pd
import numpy as np
import scipy.stats
from pandas import ExcelWriter

exp_matrix = pd.DataFrame(np.zeros((11, 11)))
act_matrix = pd.DataFrame(np.zeros((11, 11)))

act_exp_outcome = pd.DataFrame(np.zeros((3, 2)))

def exp_act_results(year_vector,serie_vector):

    for i in range(0,len(year_vector)):
        for j in range(0,len(serie_vector)):

            c.execute("SELECT EXP_GOAL1, EXP_GOAL2, ACT_GOAL1, ACT_GOAL2 FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ?",[year_vector[i], serie_vector[j]])
            ev_matrix = c.fetchall()

            for k in range(0,len(ev_matrix)):

                if ev_matrix[k][2] + ev_matrix[k][3] < 11:
                    act_matrix[ev_matrix[k][2]][ev_matrix[k][3]] += 1

                    if ev_matrix[k][2] > ev_matrix[k][3]:
                        act_exp_outcome[0][0] += 1
                    elif ev_matrix[k][2] == ev_matrix[k][3]:
                        act_exp_outcome[0][1] += 1
                    else:
                        act_exp_outcome[0][2] += 1

                    for m1 in range(0,10):
                        for m2 in range(0,10):

                            if m1+m2 < 11:
                                exp_matrix[m1][m2] += scipy.stats.distributions.poisson.pmf(m1,ev_matrix[k][0]) * scipy.stats.distributions.poisson.pmf(m2, ev_matrix[k][1])

                                if m1 > m2:
                                    act_exp_outcome[1][0] += scipy.stats.distributions.poisson.pmf(m1,ev_matrix[k][0]) * scipy.stats.distributions.poisson.pmf(m2, ev_matrix[k][1])
                                elif m1 == m2:
                                    act_exp_outcome[1][1] += scipy.stats.distributions.poisson.pmf(m1,ev_matrix[k][0]) * scipy.stats.distributions.poisson.pmf(m2, ev_matrix[k][1])
                                else:
                                    act_exp_outcome[1][2] += scipy.stats.distributions.poisson.pmf(m1,ev_matrix[k][0]) * scipy.stats.distributions.poisson.pmf(m2, ev_matrix[k][1])

def exp_act_nGoals(year_vector, serie_vector):

    act_goals = 0
    exp_goals = 0

    exp_act_goals = []

    for i in range(0, len(year_vector)):
        for j in range(0, len(serie_vector)):

            c.execute("SELECT SEASON, SERIE, SUM(EXP_GOAL1), SUM(EXP_GOAL2), SUM(ACT_GOAL1), SUM(ACT_GOAL2) FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND SERIE = ? GROUP BY SEASON, SERIE ORDER BY SERIE, SEASON",[year_vector[i], serie_vector[j]])

            exp_act_goals.append(c.fetchall())


    return np.array(exp_act_goals)

def home_goal_by_exp_goal():
    c.execute("SELECT ROUND(EXP_GOAL1*10) EXPG, COUNT(EXP_GOAL1) AS N, SUM(ACT_GOAL1*10)/COUNT(ACT_GOAL1) AS ACT_GOAL1 FROM EXP_SHOTS_TABLE GROUP BY EXPG ORDER BY EXPG DESC")
    return(c.fetchall())

def away_goal_by_exp_goal():
    c.execute("SELECT ROUND(EXP_GOAL2*10) EXPG, COUNT(EXP_GOAL2) AS N, SUM(ACT_GOAL2*10)/COUNT(ACT_GOAL2) AS ACT_GOAL1 FROM EXP_SHOTS_TABLE GROUP BY EXPG ORDER BY EXPG DESC")
    return(c.fetchall())

exp_act_results([2015,2016,2017,2018,2019],['SHL','HA'])

print(exp_act_nGoals([2015,2016,2017,2018,2019],['SHL','HA']))

print(act_exp_outcome)

print(act_matrix)
print(exp_matrix)

hgbeg = home_goal_by_exp_goal()
agbeg = away_goal_by_exp_goal()

writer = ExcelWriter('model_evaluation.xlsx')

act_matrix.to_excel(writer,'Act_matrix')
exp_matrix.to_excel(writer,'Exp_matrix')
act_exp_outcome.to_excel(writer,'Act_exp_outcome')
pd.DataFrame(hgbeg).to_excel(writer,'Home goal by exp goal')
pd.DataFrame(agbeg).to_excel(writer,'Away goal by exp goal')


writer.save()