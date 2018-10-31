import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from create_pre_match_tables import create_pre_match_table
from create_pre_match_tables import get_expected_shots
from model_game_shots import get_shots_goals_linreg
from model_shot_efficiency import get_efficiency_model_linreg
from create_pre_match_tables import get_team_players
from pandas import ExcelWriter
from create_pre_match_tables import get_ANN_odds
from create_pre_match_tables import update_forest_data
from create_pre_match_tables import get_inputs_forest_model
from model_outcome import get_outcome_model_forest

import pandas as pd
import numpy as np
import scipy

def get_adjusted_shots(home_shots, away_shots, hometeam, awayteam, gamedate, seasonYear):

    #Keep track on how well expected shots were calculated for the team so far

        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS1), SUM(ACT_SHOTS1) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND HOMETEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 13)",[seasonYear, hometeam, gamedate])
        hths = c.fetchall()
        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS2), SUM(ACT_SHOTS2) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND AWAYTEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 7)",[seasonYear, hometeam, gamedate])
        htas = c.fetchall()

        if hths[0][0] != 0 and htas[0][0] != 0 and hths[0][0] + htas[0][0] > 0:

            p = ((hths[0][0] + htas[0][0])/20)**(1/2)

            shot_adjust_home = (hths[0][2]+htas[0][2]) / (hths[0][1]+htas[0][1]) * p + (1-p)
        else:
            shot_adjust_home = 1

        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS1), SUM(ACT_SHOTS1) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND HOMETEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 7)",[seasonYear, awayteam, gamedate])
        aths = c.fetchall()
        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS2), SUM(ACT_SHOTS2) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND AWAYTEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 13)",[seasonYear, awayteam, gamedate])
        atas = c.fetchall()


        if aths[0][0] != 0 and atas[0][0] != 0 and aths[0][0] + atas[0][0] > 0:

            p = ((aths[0][0] + atas[0][0]) / 20)**(1/2)

            shot_adjust_away = (aths[0][2] + atas[0][2]) / (aths[0][1] + atas[0][1]) * p + (1-p)
        else:
            shot_adjust_away = 1

        home_shots *= shot_adjust_home
        away_shots *= shot_adjust_away

        return home_shots, away_shots

def get_adjusted_shots_against(home_shots, away_shots, hometeam, awayteam, gamedate, seasonYear):

    #Keep track on how well expected shots were calculated for the team so far

        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS2), SUM(ACT_SHOTS2) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND HOMETEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 13)",[seasonYear, hometeam, gamedate])
        hths = c.fetchall()
        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS1), SUM(ACT_SHOTS1) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND AWAYTEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 7)",[seasonYear, hometeam, gamedate])
        htas = c.fetchall()

        if hths[0][0] != 0 and htas[0][0] != 0 and hths[0][0] + htas[0][0] > 0:

            p = ((hths[0][0] + htas[0][0])/20)**(1/2)

            goal_adjust_away = (hths[0][2]+htas[0][2]) / (hths[0][1]+htas[0][1]) * p + (1-p)
        else:
            goal_adjust_away = 1

        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS2), SUM(ACT_SHOTS2) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND HOMETEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 7)",[seasonYear, awayteam, gamedate])
        aths = c.fetchall()
        c.execute("SELECT COUNT(GAMEID), SUM(EXP_SHOTS1), SUM(ACT_SHOTS1) FROM (SELECT * FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND AWAYTEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 13)",[seasonYear, awayteam, gamedate])
        atas = c.fetchall()


        if aths[0][0] != 0 and atas[0][0] != 0 and aths[0][0] + atas[0][0] > 0:

            p = ((aths[0][0] + atas[0][0]) / 20)**(1/2)

            goal_adjust_home = (aths[0][2] + atas[0][2]) / (aths[0][1] + atas[0][1]) * p + (1-p)
        else:
            goal_adjust_home = 1

        home_shots *= goal_adjust_home
        away_shots *= goal_adjust_away

        return home_shots, away_shots

def get_result_matrix(home_goals, away_goals):
    results = pd.DataFrame(np.zeros((11, 11)))
    odds1X2 = pd.DataFrame(np.zeros((2, 3)), columns=['1', 'X', '2'])
    odds45 = pd.DataFrame(np.zeros((2, 2)), columns=['O45', 'U45'])

    for i in range(0, 11):
        for j in range(0, 11):
            results[i][j] = scipy.stats.distributions.poisson.pmf(j,home_goals) * scipy.stats.distributions.poisson.pmf(i,away_goals)

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
                odds45['O45'][0] += results[i][j]
            else:
                odds45['U45'][0] += results[i][j]

    odds1X2['1'][1] = 1 / odds1X2['1'][0]
    odds1X2['X'][1] = 1 / odds1X2['X'][0]
    odds1X2['2'][1] = 1 / odds1X2['2'][0]

    odds45['O45'][1] = 1 / odds45['O45'][0]
    odds45['U45'][1] = 1 / odds45['U45'][0]

    return results, odds1X2, odds45

def get_result_matrix_by_search(p1,pX,p2,u45,o45,hg_sp, ag_sp):

    curr_error = 1

    hg_final = 0
    ag_final = 0


    for t1 in range(0,6):
        for t2 in range(0,6):

            hg = hg_sp + t1 * 0.05 - 0.1
            ag = ag_sp + t2 * 0.05 - 0.1

            results, odds1X2, odds45 = get_result_matrix(hg, ag)

            tot_error = 0
            tot_error += abs(p1-odds1X2['1'][0])
            tot_error += abs(pX-odds1X2['X'][0])
            tot_error += abs(p2-odds1X2['2'][0])

            tot_error += abs(u45 - odds45['U45'][0])
            tot_error += abs(o45 - odds45['O45'][0])

            if tot_error < curr_error:
                curr_error = tot_error
                hg_final = hg
                ag_final = ag

    hg_sp = hg_final
    ag_sp = ag_final

    for t1 in range(0, 6):
        for t2 in range(0, 6):

            hg = hg_sp + t1 * 0.01 - 0.02
            ag = ag_sp + t2 * 0.01 - 0.02

            results, odds1X2, odds45 = get_result_matrix(hg, ag)

            tot_error = 0
            tot_error += abs(p1 - odds1X2['1'][0])
            tot_error += abs(pX - odds1X2['X'][0])
            tot_error += abs(p2 - odds1X2['2'][0])

            tot_error += abs(u45 - odds45['U45'][0])
            tot_error += abs(o45 - odds45['O45'][0])

            if tot_error < curr_error:
                curr_error = tot_error
                hg_final = hg
                ag_final = ag

    hg_sp = hg_final
    ag_sp = ag_final

    for t1 in range(0, 6):
        for t2 in range(0, 6):

            hg = hg_sp + t1 * 0.002 - 0.004
            ag = ag_sp + t2 * 0.002 - 0.004

            results, odds1X2, odds45 = get_result_matrix(hg, ag)

            tot_error = 0
            tot_error += abs(p1 - odds1X2['1'][0])
            tot_error += abs(pX - odds1X2['X'][0])
            tot_error += abs(p2 - odds1X2['2'][0])

            tot_error += abs(u45 - odds45['U45'][0])
            tot_error += abs(o45 - odds45['O45'][0])

            if tot_error < curr_error:
                curr_error = tot_error
                hg_final = hg
                ag_final = ag

    return results



def create_pre_match_analysis(gamedate, serie, hometeam, awayteam, gameid):



    # Calculate season

    seasonYear = int(gamedate[0:4])

    if int(gamedate[5:7]) > 6:
        seasonYear += 1

    print(hometeam, awayteam)

    [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1, score_data1] = create_pre_match_table(gamedate, serie, hometeam, "H")
    [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2, score_data2] = create_pre_match_table(gamedate, serie, awayteam, "A")

    score1 = score_data1[3]
    score2 = score_data2[3]

    # Get datatables from create_pre_match_tables

    [ave_home_shots, ave_home_shots_against, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots, ave_away_shots_against, ave_score_shot_away, ave_conceded_shot_away, average_goal_percent] = get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_data1, score_data2, serie, c, gameid, gamedate, seasonYear)

    print("Scores:", score1, score2)


    ####################################################################################################################################################################
    ###                                                                         MODEL 1                                                                              ###
    ####################################################################################################################################################################


    # Get shots, first base function then adjusted function

    home_shots_temp, away_shots_temp = get_shots_goals_linreg(seasonYear, [ave_home_shots, ave_home_shots_against, ave_away_shots, ave_away_shots_against, score_data1[3], score_data2[3]], gameid, 'SHL', c)

    home_shots, away_shots = get_adjusted_shots(home_shots_temp, away_shots_temp, hometeam, awayteam, gamedate, seasonYear)

    #home_shots, away_shots = get_adjusted_shots_against(home_shots_temp2, away_shots_temp2, hometeam, awayteam, gamedate,seasonYear, c)

    print("Expected shots:", home_shots, away_shots)


    # Get goals from shots, first base function then basic adjustment

    home_goals, away_goals = get_efficiency_model_linreg(seasonYear, [home_shots, away_shots, score1-score2, average_goal_percent], gameid, 'SHL', c)

    home_goals *= 0.975 # Basic adjustment
    away_goals *= 0.995  # Basic adjustment


    # Get result matrix and match odds for model 1

    results, odds1X2_1, odds45_1 = get_result_matrix(home_goals, away_goals)

    c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, EXP_GOALS1 = ?, EXP_GOALS2 = ?, ODDS1 = ?, ODDSX = ?, ODDS2 = ? WHERE GAMEID = ?",[home_shots, away_shots, home_goals, away_goals, odds1X2_1['1'][0], odds1X2_1['X'][0], odds1X2_1['2'][0], gameid])
    conn.commit()

    c.execute("SELECT SUM(ACT_GOALS1 + ACT_GOALS2), SUM(EXP_GOALS1 + EXP_GOALS2) FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND GAMEDATE < ?",[seasonYear, gamedate])
    goals_year = c.fetchall()

    if goals_year[0][0] > 0 and goals_year[0][1] > 0:
        exp_ratio = goals_year[0][1] / goals_year[0][0]

        if goals_year[0][0] < 100:
            exp_ratio = exp_ratio ** (goals_year[0][0]/100)

        #print(exp_ratio)

    home_goals /= exp_ratio  # Adjustment based on expectency ratio
    away_goals /= exp_ratio  # Adjustment based on expectency ratio

    print("Expected goals:", home_goals, away_goals)

    results, odds1X2_1, odds45_1 = get_result_matrix(home_goals, away_goals)


    ####################################################################################################################################################################
    ###                                                                         MODEL 2                                                                              ###
    ####################################################################################################################################################################


    # Update model data
    update_forest_data(serie)

    home_team_off, home_team_def, away_team_off, away_team_def = get_inputs_forest_model(serie, seasonYear, gamedate, hometeam, awayteam)

    inputs = pd.DataFrame([[score1, score2, home_team_off, home_team_def, away_team_off, away_team_def]])

    # Get odds model 2
    odds1X2_2, odds45_2 = get_outcome_model_forest(serie, seasonYear, inputs, c)


    ####################################################################################################################################################################
    ###                                                                      Combine Models                                                                          ###
    ####################################################################################################################################################################


    final_p = pd.DataFrame([[odds1X2_1['1'][0],odds1X2_1['X'][0],odds1X2_1['2'][0]],
                               [odds1X2_2[0][0],odds1X2_2[1][0],odds1X2_2[2][0]],
                               [odds1X2_1['1'][0] / 2 + odds1X2_2[0][0] / 2, odds1X2_1['X'][0] / 2 + odds1X2_2[1][0] / 2, odds1X2_1['2'][0] / 2 + odds1X2_2[2][0] / 2]])

    final_p45 = pd.DataFrame([[odds45_1['U45'][0], odds45_1['O45'][0]],
                              [odds45_2[0][0], odds45_2[1][0]],
                              [odds45_1['U45'][0]/2 + odds45_2[0][0]/2, odds45_1['O45'][0]/2 + odds45_2[1][0]/2]])

    final_p[3] = 1 / final_p[0]
    final_p[4] = 1 / final_p[1]
    final_p[5] = 1 / final_p[2]

    final_p45[2] = 1 / final_p45[0]
    final_p45[3] = 1 / final_p45[1]

    print(final_p)
    print(final_p45)

    results = get_result_matrix_by_search(final_p[0][2],final_p[1][2],final_p[2][2],final_p45[0][2],final_p45[1][2],home_goals,away_goals)

    print(results)

    ####################################################################################################################################################################
    ###                                                               TIME FOR PLAYERS DATA NOW                                                                      ###
    ####################################################################################################################################################################

    # Get all players that played last three games

    keeper_stat_home, player_stat = get_team_players(hometeam, gamedate, seasonYear)
    keeper_stat_away, player_stat = get_team_players(awayteam, gamedate, seasonYear)

    return results, odds1X2_1, odds45_1, home_goals, away_goals, keeper_stat_home, keeper_stat_away

