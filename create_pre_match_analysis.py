import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

import math
import pandas as pd
import numpy as np
import scipy

from pre_match_functions import get_form
from pre_match_functions import get_strength
from pre_match_functions import getOdds1X2
from pre_match_functions import getOdds55
from pre_match_functions import get_player_form
from pre_match_functions import get_team_schedule
from pre_match_functions import get_offence_info
from pre_match_functions import get_defence_info
from pre_match_functions import get_stats
from pre_match_functions import create_tables
from create_pre_match_tables import create_pre_match_table
from create_pre_match_tables import create_outcome_predicter_table
from create_pre_match_tables import get_expected_shots
from calcFunctions import calculate_team_strength
from adhoc.linreg_shots import update_season_shots_goals
from create_pre_match_tables import get_shots_goals



def create_pre_match_analysis(gamedate, serie, hometeam, awayteam, gameid):
    [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1, schedule_data1, score_data1] = create_pre_match_table(gamedate, serie, hometeam, "H")
    [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2, schedule_data2, score_data2] = create_pre_match_table(gamedate, serie, awayteam, "A")

    seasonYear = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        seasonYear +=1

    #create_outcome_predicter_table(base_table1, full_data1, full_data2, home_data1, away_data2, schedule_data1, schedule_data2, score_data1, score_data2, last_five_data1, last_five_data2, gameid)

    print(hometeam, awayteam)

    [ave_home_shots, ave_home_shots_against, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots, ave_away_shots_against, ave_score_shot_away, ave_conceded_shot_away] = get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_data1, score_data2, serie, c, gameid, gamedate, seasonYear)

    #Recalibrate regression on shots

    if 1 == 2:

        update_season_shots_goals(serie, seasonYear, c)

        c.execute("SELECT INT1, INT2, C11, C12, C13, C21, C22, C23 FROM EXP_SHOTS_TABLE WHERE SEASON = ? ORDER BY GAMEID DESC",[seasonYear])
        p = c.fetchall()

        shots_list = [0, ave_home_shots, ave_home_shots_against, ave_away_shots, ave_away_shots_against, score_data1[0], score_data2[0]]

        exp_home_shots, exp_away_shots = get_shots_goals(p[0][0], p[0][2], p[0][3], p[0][4], p[0][1], p[0][5], p[0][6], p[0][7], shots_list)

        print(exp_home_shots, exp_away_shots)

        #Create result dataframe

        results = pd.DataFrame(np.zeros((11, 11)))

        for i in range(0,11):
            for j in range(0,11):

                results[i][j] = scipy.stats.distributions.poisson.pmf(j, exp_home_goals) * scipy.stats.distributions.poisson.pmf(i, exp_away_goals)



#c.execute("SELECT GAMEDATE, SERIE, TEAM, OPPONENT, GAMEID FROM TEAMGAMES WHERE (SEASONID = ? OR SEASONID = ?) AND SERIE = ? AND HOMEAWAY = ?",[2017, 2017, 'HA', 'H'])
#lst = c.fetchall()

#for i in range(0,len(lst)):

#    create_pre_match_analysis(lst[i][0],lst[i][1],lst[i][2],lst[i][3],lst[i][4])
#    print(lst[i][4],"loaded")


create_pre_match_analysis('2018-10-18','SHL',"Skellefteå AIK","Djurgårdens IF","")
create_pre_match_analysis('2018-10-18','SHL',"Örebro HK","Färjestad BK","")
create_pre_match_analysis('2018-10-18','SHL',"Växjö Lakers HC","HV 71","")
create_pre_match_analysis('2018-10-18','SHL',"IF Malmö Redhawks","Brynäs IF","")
create_pre_match_analysis('2018-10-18','SHL',"Timrå IK","Rögle BK","")
create_pre_match_analysis('2018-10-18','SHL',"Frölunda HC","Luleå HF","")

#create_pre_match_analysis('2018-10-02','SHL',"Linköping HC","BrynäsIF","")
#create_pre_match_analysis('2018-10-04','SHL',"Linköping HC","Mora IK","")
#create_pre_match_analysis('2018-10-06','SHL',"Färjestad BK","Linköping HC","")
#create_pre_match_analysis('2018-10-11','SHL',"Linköping HC","Timrå IK","")



conn.commit()