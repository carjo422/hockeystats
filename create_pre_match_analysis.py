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

    [ave_home_shots, ave_home_shots_against, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots, ave_away_shots_against, ave_score_shot_away, ave_conceded_shot_away] = get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_data1, score_data2, serie, c, gameid, gamedate, seasonYear)

    home_shots, away_shots = get_shots_goals_linreg(seasonYear,[ave_home_shots, ave_home_shots_against, ave_away_shots, ave_away_shots_against, score_data1[0], score_data2[0]], gameid,c)

    print(home_shots, away_shots)

    home_goals, away_goals = get_efficiency_model_linreg(seasonYear, [home_shots, away_shots, score_data1[0], score_data2[0]], gameid,c)

    print(home_goals, away_goals)

    #Create result dataframe

    results = pd.DataFrame(np.zeros((11, 11)))

    for i in range(0,11):
        for j in range(0,11):
            results[i][j] = scipy.stats.distributions.poisson.pmf(j, home_goals) * scipy.stats.distributions.poisson.pmf(i, away_goals)

    print(results)



#c.execute("SELECT GAMEDATE, SERIE, TEAM, OPPONENT, GAMEID FROM TEAMGAMES WHERE (SEASONID = ? OR SEASONID = ?) AND SERIE = ? AND HOMEAWAY = ?",[2018, 2019, 'SHL', 'H'])
#lst = c.fetchall()

#for i in range(0,len(lst)):

#    create_pre_match_analysis(lst[i][0],lst[i][1],lst[i][2],lst[i][3],lst[i][4])
#    print(lst[i][4],"loaded")


create_pre_match_analysis('2018-10-21','SHL',"Linköping HC","Skellefteå AIK","393415")

conn.commit()