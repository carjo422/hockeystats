import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from create_pre_match_tables import create_pre_match_table
from create_pre_match_tables import get_expected_shots
from model_game_shots import get_shots_goals_linreg
from model_shot_efficiency import get_efficiency_model_linreg

import pandas as pd
import numpy as np
import scipy


def create_pre_match_analysis(gamedate, serie, hometeam, awayteam, gameid):
    [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1, score_data1] = create_pre_match_table(gamedate, serie, hometeam, "H")
    [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2, score_data2] = create_pre_match_table(gamedate, serie, awayteam, "A")

    seasonYear = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        seasonYear +=1

    print(hometeam, awayteam)

    [ave_home_shots, ave_home_shots_against, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots, ave_away_shots_against, ave_score_shot_away, ave_conceded_shot_away, average_goal_percent] = get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_data1, score_data2, serie, c, gameid, gamedate, seasonYear)

    home_shots, away_shots = get_shots_goals_linreg(seasonYear,[ave_home_shots, ave_home_shots_against, ave_away_shots, ave_away_shots_against, score_data1[3], score_data2[3]], gameid, serie, c)

    print("Scores:", score_data1[3], score_data2[3])

    #Keep track on how well expected shots were calculated for the team so far

    c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS1), SUM(ACT_SHOTS1) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND HOMETEAM = ? ORDER BY GAMEDATE DESC LIMIT 13)",[seasonYear, hometeam])
    hths = c.fetchall()
    c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS2), SUM(ACT_SHOTS2) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND AWAYTEAM = ? ORDER BY GAMEDATE DESC LIMIT 7)",[seasonYear, hometeam])
    htas = c.fetchall()

    if hths[0][0] != None and htas[0][0] != None and hths[0][0] + htas[0][0] > 0:

        p = ((hths[0][0] + htas[0][0])/20)**(1/2)

        shot_adjust_home = (hths[0][2]+htas[0][2]) / (hths[0][1]+htas[0][1]) * p + (1-p)
    else:
        shot_adjust_home = 1

    c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS1), SUM(ACT_SHOTS1) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND HOMETEAM = ? ORDER BY GAMEDATE DESC LIMIT 7)",[seasonYear, awayteam])
    aths = c.fetchall()
    c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS2), SUM(ACT_SHOTS2) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND AWAYTEAM = ? ORDER BY GAMEDATE DESC LIMIT 13)",[seasonYear, awayteam])
    atas = c.fetchall()

    if aths[0][0] != None and atas[0][0] != None and aths[0][0] + atas[0][0] > 0:

        p = ((aths[0][0] + atas[0][0]) / 20)**(1/2)

        shot_adjust_away = (aths[0][2] + atas[0][2]) / (aths[0][1] + atas[0][1]) * p + (1-p)
    else:
        shot_adjust_away = 1

    home_shots *= shot_adjust_home
    away_shots *= shot_adjust_away

    print("Expected shots:", home_shots, away_shots)

    home_goals, away_goals = get_efficiency_model_linreg(seasonYear, [home_shots, away_shots, score_data1[3]-score_data2[3],average_goal_percent], gameid, serie, c)

    print(home_goals / home_shots, away_goals / away_shots)

    # Adjust goals to get to lower level

    home_goals *= 0.95
    away_goals *= 0.98

    #Check how the model predicted home and away goals so far this season

    c.execute("SELECT COUNT(GAMEID), SUM(EXP_GOALS1), SUM(EXP_GOALS2), SUM(ACT_GOALS1), SUM(ACT_GOALS2) FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND GAMEDATE < ?",[seasonYear, gamedate])
    model_adjust = c.fetchall()



    print("Expected goals:", home_goals, away_goals)

    #Create result dataframe

    results = pd.DataFrame(np.zeros((11, 11)))
    odds1X2 = pd.DataFrame(np.zeros((2, 3)),columns = ['1','X','2'])
    odds45 = pd.DataFrame(np.zeros((2, 2)),columns = ['45_O','45_U'])



    for i in range(0,11):
        for j in range(0,11):
            results[i][j] = scipy.stats.distributions.poisson.pmf(j, home_goals) * scipy.stats.distributions.poisson.pmf(i, away_goals)

    results[0][0] *= 1.5
    results[1][1] *= 1.35
    results[2][2] *= 1.12
    results[3][3] *= 1.35

    results[0][1] *= 0.75
    results[1][2] *= 0.75
    results[2][3] *= 0.75
    results[3][4] *= 0.7
    results[4][5] *= 0.6
    results[5][6] *= 0.5

    results[1][0] *= 0.75
    results[2][1] *= 0.75
    results[3][2] *= 0.75
    results[4][3] *= 0.7
    results[5][4] *= 0.6
    results[6][5] *= 0.5

    results[0][2] *= 1.1
    results[1][3] *= 1.1
    results[2][4] *= 1.1
    results[3][5] *= 1.1

    results[2][0] *= 1.1
    results[3][1] *= 1.1
    results[4][2] *= 1.1
    results[5][3] *= 1.1

    results[0][3] *= 1.3
    results[1][4] *= 1.3
    results[2][5] *= 1.2
    results[3][6] *= 1.2

    results[3][0] *= 1.2
    results[4][1] *= 1.3
    results[5][2] *= 1.2
    results[6][3] *= 1.2

    results[5][0] *= 1.05
    results[6][0] *= 1.3
    results[7][0] *= 1.5

    results[0][4] *= 1.5
    results[0][5] *= 1.3
    results[0][6] *= 1.2

    results[1][5] *= 1.3
    results[1][6] *= 1.3

    d = results.values.sum()

    for i in range(0, 11):
        for j in range(0, 11):

            results[i][j] /= d

            if i == j:
                odds1X2['X'] += results[i][j]
            elif i < j:
                odds1X2['1'] += results[i][j]
            else:
                odds1X2['2'] += results[i][j]

            if i + j > 4.5:
                odds45['45_O'] += results[i][j]
            else:
                odds45['45_U'] += results[i][j]


    odds1X2['1'][1] = 1/odds1X2['1'][0]
    odds1X2['X'][1] = 1/odds1X2['X'][0]
    odds1X2['2'][1] = 1/odds1X2['2'][0]

    print(odds1X2)
    print(odds45)





c.execute("SELECT GAMEDATE, SERIE, TEAM, OPPONENT, GAMEID FROM TEAMGAMES WHERE (SEASONID = ? OR SEASONID = ?) AND SERIE = ? AND HOMEAWAY = ?",[2019, 2019, 'SHL', 'H'])
lst = c.fetchall()

#for i in range(0,len(lst)):

#    create_pre_match_analysis(lst[i][0],lst[i][1],lst[i][2],lst[i][3],lst[i][4])
#    print(lst[i][4],"loaded")



create_pre_match_analysis('2018-10-23','SHL',"HV 71","Mora IK","")

conn.commit()