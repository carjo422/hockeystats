
from create_pre_match_tables import create_pre_match_table
from create_pre_match_tables import get_expected_shots
from model_game_shots import get_shots_goals_linreg
from model_shot_efficiency import get_efficiency_model_linreg
from pandas import ExcelWriter
#import openpyxl
#from openpyxl import load_workbook

from create_pre_match_tables import get_ANN_odds
from create_pre_match_tables import update_model1_data
from create_pre_match_tables import update_model2_data
from create_pre_match_tables import get_model1_data
from model_outcome import get_outcome_model1
from create_pre_match_tables import get_model2_data
from model_outcome import get_outcome_model2
from model_nGoals import get_nGoals_model
from create_player_tables import get_player_data
from create_player_tables import get_keeper_data
from model_goal_scorer import get_goal_scorer
from scfiles.get_lineups import get_lineups
from calcFunctions import calculate_team_strength
from scfiles.get_live_games import get_live_games

import pandas as pd
import numpy as np
import scipy

def get_adjusted_shots(home_shots, away_shots, hometeam, awayteam, gamedate, seasonYear, c, conn):

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

def get_adjusted_shots_against(home_shots, away_shots, hometeam, awayteam, gamedate, seasonYear, c, conn):

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


    #print("Expected goals after matrix: ", exp_goals1, exp_goals2)

    return results, odds1X2, odds45

def get_starting_keeper(team, lineup):

    starting_keeper = ["",""]

    for i in range(0, len(lineup)):
        if lineup[i][1] == team and lineup[i][5] == 'Goalies':
            if lineup[i][6] == 1:
                starting_keeper = [lineup[i][3], lineup[i][4]]

    return starting_keeper

def get_model1_features(player_stat, c):

    player_stat['Pos_Score_Final'] = player_stat['Pos Score'] * player_stat['Pos multiplier']
    player_stat['Pos_Score_Final_Last'] = player_stat['Pos Score Last'] * player_stat['Pos multiplier']
    player_stat['Hist_Scoring_Reg_Final'] = (player_stat['Score ratio'] * player_stat['Hist Score Reg'] * player_stat['Weight'] +
                                             player_stat['Pos_Score_Final'] * 5) / (player_stat['Weight'] + 5)
    player_stat['Hist_Scoring_PP_Final'] = (player_stat['Hist Score PP'] * player_stat['Weight'] + player_stat[
        'Pos_Score_Final'] * 5) / (player_stat['Weight'] + 5)

    model_data = player_stat[['Pos_Score_Final', 'Pos_Score_Final_Last', 'Hist Score']]
    model_data = model_data.sort_index()

    score_percent = get_goal_scorer(model_data,c)

    player_output = player_stat[['Forname','Surname','Pos_Score_Final','Pos_Score_Final_Last', 'Hist Score']]
    player_output = player_output.sort_index()

    player_output['Goal percent'] = score_percent
    #player_output.sort_values(['Goal percent'], ascending = [0])

    return player_output




def create_pre_match_analysis(gamedate, seasonID, serie, hometeam, awayteam, gameid, c, conn):


    # Calculate season

    seasonYear = int(gamedate[0:4])

    if int(gamedate[5:7]) > 6:
        seasonYear += 1

    modelSeasonYear = seasonYear
    #Code to use newer models on old data if no old model is available
    if modelSeasonYear < 2017:
        modelSeasonYear = 2017

    print(serie, hometeam, awayteam, gamedate)

    [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1, score_data1] = create_pre_match_table(gamedate, serie, hometeam, "H", c, conn)
    [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2, score_data2] = create_pre_match_table(gamedate, serie, awayteam, "A", c, conn)

    score1 = score_data1[3]
    score2 = score_data2[3]

    # Get datatables from create_pre_match_tables

    [ave_home_shots, ave_home_shots_against, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots, ave_away_shots_against, ave_score_shot_away, ave_conceded_shot_away, average_goal_percent] = get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_data1, score_data2, serie, c, conn, gameid, gamedate, seasonYear)

    print("Scores:", score1, score2)

    if gameid == "":
        gameid = get_live_games(seasonID, gamedate, hometeam, awayteam)

    curr_lineup = []
    starting_keeper_home = ["",""]
    starting_keeper_away = ["",""]

    #Get the correct lineup if available, recalculate scores based on lineup
    if gameid != "":
        curr_lineup = get_lineups(gameid, 0, "", seasonYear, hometeam, awayteam)

        new_score1 = 0
        new_score2 = 0

        new_score1 = calculate_team_strength(hometeam, gamedate, curr_lineup, c)
        new_score2 = calculate_team_strength(awayteam, gamedate, curr_lineup, c)

        print("New Scores:", new_score1[3], new_score2[3])
        score1 = new_score1[3]
        score2 = new_score2[3]

        #Get starting keeper
        starting_keeper_home = get_starting_keeper(hometeam, curr_lineup)
        starting_keeper_away = get_starting_keeper(awayteam, curr_lineup)

    # Get actual scores

    act_home_goals = 0
    act_away_goals = 0

    c.execute("SELECT HSCORE1 + HSCORE2 + HSCORE3, ASCORE1 + ASCORE2 + ASCORE3 FROM STATS WHERE GAMEID = ?",[gameid])
    scores = c.fetchall()

    if len(scores) > 0:
        act_home_goals = scores[0][0]
        act_away_goals = scores[0][1]


    ####################################################################################################################################################################
    ###                                                                  MODEL nGOALS FOR 1 & 2                                                                      ###
    ####################################################################################################################################################################

    home_team_off, home_team_def, away_team_off, away_team_def = get_model1_data(serie, modelSeasonYear, gamedate, hometeam, awayteam, c, conn)
    inputs = pd.DataFrame([[abs(score1/score2-1), home_team_off, away_team_off, home_team_def, away_team_def]])

    nGoals = get_nGoals_model(seasonYear, inputs, c)

    print("nGoals: ", nGoals)

    ####################################################################################################################################################################
    ###                                                                         MODEL 1                                                                              ###
    ####################################################################################################################################################################


    # Get shots, first base function then adjusted function

    home_shots_temp, away_shots_temp = get_shots_goals_linreg(modelSeasonYear, [ave_home_shots, ave_home_shots_against, ave_away_shots, ave_away_shots_against, score_data1[3], score_data2[3]], gameid, serie, c, conn)

    home_shots, away_shots = get_adjusted_shots(home_shots_temp, away_shots_temp, hometeam, awayteam, gamedate, seasonYear, c, conn)

    #home_shots, away_shots = get_adjusted_shots_against(home_shots_temp2, away_shots_temp2, hometeam, awayteam, gamedate,seasonYear, c, conn)

    #print("Expected shots:", home_shots, away_shots)


    # Get goals from shots, first base function then basic adjustment

    home_goals1, away_goals1 = get_efficiency_model_linreg(modelSeasonYear, [home_shots, away_shots, score1-score2, average_goal_percent], gameid, serie, c)

    home_goals1 *= 0.975 # Basic adjustment
    away_goals1 *= 0.995  # Basic adjustment

    print("Model 1 expected goals:", home_goals1, away_goals1)

    ####################################################################################################################################################################
    ###                                                                         MODEL 2                                                                              ###
    ####################################################################################################################################################################


    # Update model data
    #update_forest_data_1(serie, c, conn) #(If historic values need to be rerun for model)

    home_team_off, home_team_def, away_team_off, away_team_def = get_model1_data(serie, modelSeasonYear, gamedate, hometeam, awayteam, c, conn)

    inputs = pd.DataFrame([[home_team_off, home_team_def, away_team_off, away_team_def]])  #
    #print(inputs)

    # Get odds model 2
    diff1 = get_outcome_model1(serie, modelSeasonYear, inputs, c)  # seasonYear = 2019
    #print(diff1)

    home_goals2 = nGoals/2+diff1/2
    away_goals2 = nGoals/2-diff1/2

    print("Model 2 expected goals:", home_goals2, away_goals2)


    ####################################################################################################################################################################
    ###                                                                         MODEL 3                                                                              ###
    ####################################################################################################################################################################


    # Update model data
    #update_forest_data_2(serie, seasonYear, c, conn) #(If historic values need to be rerun for model)

    comb_score_home = get_model2_data(score1, full_data1, home_data1, last_five_data1, last_match_data1,'H')
    comb_score_away = get_model2_data(score2, full_data2, away_data2, last_five_data2, last_match_data2,'A')

    #print("Comb scores:", comb_score_home, comb_score_away)

    inputs = pd.DataFrame([[comb_score_home, comb_score_away]])

    # Get odds model 3
    diff2 = get_outcome_model2(serie, modelSeasonYear, inputs, c)  # seasonYear = 2019

    home_goals3 = nGoals/2+diff2/2
    away_goals3 = nGoals/2-diff2/2

    print("Model 3 expected goals:", home_goals3, away_goals3)

    ####################################################################################################################################################################
    ###                                                                       COMBINE MODELS                                                                         ###
    ####################################################################################################################################################################


    home_goals = home_goals1*5/10+home_goals2*2/10+home_goals3*3/10
    away_goals = away_goals1*5/10+away_goals2*2/10+away_goals3*3/10

    results, odds1X2, odds45 = get_result_matrix(home_goals, away_goals)


    c.execute("UPDATE EXP_SHOTS_TABLE SET EXP_SHOTS1 = ?, EXP_SHOTS2 = ?, EXP_GOALS1 = ?, EXP_GOALS2 = ?, ODDS1 = ?, ODDSX = ?, ODDS2 = ? WHERE GAMEID = ?",[home_shots, away_shots, home_goals, away_goals, odds1X2['1'][0], odds1X2['X'][0], odds1X2['2'][0], gameid])
    conn.commit()

    c.execute("SELECT SUM(ACT_GOALS1 + ACT_GOALS2), SUM(EXP_GOALS1 + EXP_GOALS2) FROM EXP_SHOTS_TABLE WHERE SEASON = ? AND GAMEDATE < ? AND SERIE = ?",[seasonYear, gamedate, serie])
    goals_year = c.fetchall()

    exp_ratio = 1

    if goals_year[0][0] != None and goals_year[0][1] != None:

        if goals_year[0][0] > 0 and goals_year[0][1] > 0:
            exp_ratio = goals_year[0][1] / goals_year[0][0]

            if goals_year[0][0] < 100:
                exp_ratio = exp_ratio ** (goals_year[0][0]/100)

    exp_ratio = (exp_ratio-1)/4+1

    print("Exp ratio", exp_ratio)

    home_goals /= exp_ratio  # Adjustment based on expectency ratio
    away_goals /= exp_ratio  # Adjustment based on expectency ratio

    print("Expected goals combined models:", home_goals, away_goals)

    # Get result matrix and match odds

    results, odds1X2, odds45 = get_result_matrix(home_goals, away_goals)
    result_odds = 1 / results

    #print(result_odds)

    print(odds1X2)
    print(odds45)

    ####################################################################################################################################################################
    ###                                                               TIME FOR PLAYERS DATA NOW                                                                      ###
    ####################################################################################################################################################################

    # Get keeper stats

    keeper_stat_home = get_keeper_data(hometeam, gamedate, seasonYear, c, conn)
    keeper_stat_away = get_keeper_data(awayteam, gamedate, seasonYear, c, conn)

    #If available get the correct keepers to start
    if starting_keeper_home[0] != "":
        keeper_stat_home = keeper_stat_home[keeper_stat_home['Forname'] == starting_keeper_home[0]]
        keeper_stat_home = keeper_stat_home[keeper_stat_home['Surname'] == starting_keeper_home[1]]
    else:
        keeper_stat_home = keeper_stat_home[keeper_stat_home['Forname'] == "GK"]

    if starting_keeper_away[0] != "":
        keeper_stat_away = keeper_stat_away[keeper_stat_away['Forname'] == starting_keeper_away[0]]
        keeper_stat_away = keeper_stat_away[keeper_stat_away['Surname'] == starting_keeper_away[1]]
    else:
        keeper_stat_away = keeper_stat_away[keeper_stat_away['Forname'] == "GK"]

    print(keeper_stat_home.to_string())
    print(keeper_stat_away.to_string())

    # Get player stats

    cl_home = pd.DataFrame()
    cl_away = pd.DataFrame()

    #if there are lineups ready add them here

    if curr_lineup != []:
        cl = pd.DataFrame(curr_lineup, columns=['Gameid','Team','Number','Forname', 'Surname', 'Line','Starting','Audience','Venue','Season'])
        cl['Personnr'] = ""
        cl_home = cl[['Forname','Surname','Personnr','Line']][cl['Team'] == hometeam]
        cl_away = cl[['Forname', 'Surname', 'Personnr', 'Line']][cl['Team'] == awayteam]


    home_player_stat = get_player_data(hometeam, gameid, gamedate, odds1X2['1'][0], keeper_stat_away, seasonYear, serie, cl_home, c, conn)
    away_player_stat = get_player_data(awayteam, gameid, gamedate, odds1X2['2'][0], keeper_stat_home, seasonYear, serie, cl_away, c, conn)

    print(home_player_stat.to_string())
    print(away_player_stat.to_string())

    model1_home = get_model1_features(home_player_stat, c)
    model1_away = get_model1_features(away_player_stat, c)

    print(model1_home.to_string())
    print(model1_away.to_string())

    return results, odds1X2, odds45, home_goals, away_goals, act_home_goals, act_away_goals#, keeper_stat_home, keeper_stat_away

