import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

import math

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
from calcFunctions import calculate_team_strength

def create_pre_match_analysis(gamedate, serie, hometeam, awayteam, gameid):
    [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1, schedule_data1, score_data1] = create_pre_match_table(gamedate, serie, hometeam, "H")
    [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2, schedule_data2, score_data2] = create_pre_match_table(gamedate, serie, awayteam, "A")

    if len(full_data1) > 0 and len(full_data2) > 0:
        hwpt = full_data1[0][1] / full_data1[0][0]
        hdpt = (full_data1[0][2] + full_data1[0][3]) / full_data1[0][0]
        hlpt = full_data1[0][4] / full_data1[0][0]
        hggt = full_data1[0][5] / full_data1[0][0]/4
        hggpt = full_data1[0][5] / (full_data1[0][5]+full_data1[0][6])
        hsgt = full_data1[0][9] / full_data1[0][0]/50
        hsgpt = full_data1[0][9] / (full_data1[0][9] + full_data1[0][10])

        awpt = full_data2[0][1] / full_data2[0][0]
        adpt = (full_data2[0][2] + full_data2[0][3]) / full_data2[0][0]
        alpt = full_data2[0][4] / full_data2[0][0]
        aggt = full_data2[0][5] / full_data2[0][0]/4
        aggpt = full_data2[0][5] / (full_data2[0][5] + full_data2[0][6])
        asgt = full_data2[0][9] / full_data2[0][0]/50
        asgpt = full_data2[0][9] / (full_data2[0][9] + full_data2[0][10])

        if schedule_data2[0] > 0:
            schedRatio = math.log(schedule_data1[0]/schedule_data2[0])
        else:
            schedRatio = 0

        if schedRatio > 1:
            schedRatio = 1

        hscore = score_data1[3]/10
        ascore = score_data2[3]/10

        hpenalty = last_five_data1[0][7]/last_five_data1[0][0]
        apenalty = last_five_data2[0][7]/last_five_data2[0][0]

        c.execute("SELECT CASE WHEN OUTCOME = 1 THEN 1 WHEN OUTCOME = 2 or OUTCOME = 3 THEN 2 ELSE 3 END AS OUTCOME FROM TEAMGAMES WHERE GAMEID = ? AND TEAM = ?", [gameid, base_table1[3]])

        outcome = c.fetchall()[0][0]


        out1=0
        out2=0
        out3=0

        if outcome == 1:
            out1 = 1
        elif outcome == 2:
            out2 = 1
        else:
            out3 = 1

        c.execute("SELECT GAMEID FROM OUTCOME_PREDICTER WHERE GAMEID = ?",[gameid])
        chk = c.fetchall()

        if len(chk) == 0:
            c.execute("""INSERT INTO OUTCOME_PREDICTER (GAMEID, HWPT, HDPT, HLPT, HGGT, HGGPT, HSGT, HSGPT, AWPT, ADPT, ALPT, AGGT, AGGPT, ASGT, ASGPT, HSCORE, ASCORE, HPENALTY, APENALTY, SCHEDULE_RATIO, OUT1, OUT2, OUT3) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      [gameid, hwpt, hdpt, hlpt, hggt, hggpt, hsgt, hsgpt, awpt, adpt, alpt, aggt, aggpt, asgt, asgpt, hscore, ascore, hpenalty, apenalty, schedRatio, out1, out2, out3])
        else:
            pass

        conn.commit()

    if 2==1:
        seasonYear = int(gamedate[0:4])
        if int(gamedate[5:7]) > 6:
            seasonYear += 1

        [strength1, offStrength1, defStrength1] = get_strength(hometeam, seasonYear, gamedate, c)
        [strenght2, offStrength2, defStrength2] = get_strength(awayteam, seasonYear, gamedate, c)



        [form, offForm1, defForm1, hpoints5, hgoals5, conc5, hpoints3, hgoals3, hgoals1, hpoints1, hgoals1, hconc1 ,h_n_matches5] = get_form(hometeam,seasonYear,gamedate,c)
        [form, offForm2, defForm2, apoints5, agoals5, conc5, apoints3, agoals3, agoals1, apoints1, agoals1, aconc1 ,a_n_matches5] = get_form(awayteam, seasonYear,gamedate,c)

        c.execute("SELECT gamedate from teamgames where team = ? order by gamedate DESC",[hometeam])
        htd = c.fetchall()
        gamedate_pre_h = htd[0][0]

        c.execute("SELECT gamedate from teamgames where team = ? order by gamedate DESC", [awayteam])
        atd = c.fetchall()
        gamedate_pre_a = atd[0][0]

        [home_score, home_points, home_season_points, home_player_score_final] = calculate_team_strength(hometeam, gamedate_pre_h, c)
        [away_score, away_points, away_season_points, away_player_score_final] = calculate_team_strength(awayteam, gamedate_pre_a, c)

        [odds1, oddsX, odds2] = getOdds1X2(home_score,away_score)
        [prob4, prob5, prob6] = getOdds55(offForm1, defForm1, offForm2, defForm2)

        hstats1 = get_stats(hometeam, seasonYear, gamedate_pre_h, c)
        astats1  = get_stats(hometeam, seasonYear, gamedate_pre_h, c)

        [hplayers, hplayers1, hplayers5] = get_player_form(hometeam, seasonYear, gamedate, c)
        [aplayers, aplayers1, aplayers5] = get_player_form(awayteam, seasonYear, gamedate, c)

        [full_table, home_table, away_table, score_table, con_table, shots_table, penalty_table, pp_table, pp_percent_table] = create_tables(seasonYear, serie, c)

        # Offence
        off_info = get_offence_info(hometeam, offForm1, offStrength1, hgoals5, hgoals3, hgoals1, hplayers, hplayers1, hplayers5, hstats1, h_n_matches5, score_table, shots_table, pp_table, pp_percent_table)
        off_info = get_offence_info(awayteam, offForm2, offStrength2, agoals5, agoals3, agoals1, aplayers, aplayers1, aplayers5, astats1, a_n_matches5, score_table, shots_table, pp_table, pp_percent_table)

        def_info = get_defence_info(hometeam, awayteam, defStrength1, hconc1, hplayers, hplayers1, hplayers5, hstats1, h_n_matches5, con_table, penalty_table, pp_percent_table)
        def_info = get_defence_info(awayteam, hometeam, defStrength2, aconc1, aplayers, aplayers1, aplayers5, astats1, a_n_matches5, con_table, penalty_table, pp_percent_table)

        # Defence
        # Goalie
        # Powerplay
        # Boxplay
        # Overall

        #Goal scorers
        #Målvakt
        #Bäst form
        #Svag form
        #Största stjärnor
        #To score

        schedule_home = (get_team_schedule(hometeam, seasonYear, gamedate, c))
        schedule_away = (get_team_schedule(awayteam, seasonYear, gamedate, c))


    #TEST DATA ON TWO SEASONS

    c.execute("SELECT GAMEID, SEASONID, SERIE FROM SCHEDULE WHERE (SEASONID = ? OR SEASONID = ?) AND SERIE = ?",[2017,2018,'SHL'])
    testGames = c.fetchall()

    for i in range(0, len(testGames)):
        c.execute("SELECT GAMEID, HOMETEAM, AWAYTEAM, HSCORE1 + HSCORE2 + HSCORE3 as GOALS1, ASCORE1 + ASCORE2 + ASCORE3 as GOALS2 FROM STATS WHERE GAMEID = ?",[testGames[i][0]])
        scoreStats = c.fetchall()

        if scoreStats[0][3] > scoreStats[0][4]:
            outcome = 1
        elif scoreStats[0][3] < scoreStats[0][4]:
            outcome = 3
        else:
            outcome = 2

        tscore = scoreStats[0][3] + scoreStats[0][4]

        c.execute("SELECT SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?",[testGames[i][0],scoreStats[0][1]])
        hscore = c.fetchall()
        c.execute("SELECT SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?",[testGames[i][0], scoreStats[0][2]])
        ascore = c.fetchall()


        c.execute("SELECT GAMEID FROM TEST_DATA_GAME WHERE GAMEID = ?",[testGames[i][0]])
        chk = c.fetchall()

        if len(chk) > 0:
            pass
        else:
            c.execute("INSERT INTO TEST_DATA_GAME (GAMEID, OUTCOME, HGOALS, AGOALS, TGOALS, HSCORE, HFORM, HLAST, HPLAYER, ASCORE, AFORM, ALAST, APLAYER) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",[testGames[i][0],outcome, scoreStats[0][3], scoreStats[0][4], tscore, hscore[0][0], hscore[0][1], hscore[0][2], hscore[0][3], ascore[0][0], ascore[0][1], ascore[0][2], ascore[0][3]])

        conn.commit()


c.execute("SELECT GAMEDATE, SERIE, TEAM, OPPONENT, GAMEID FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? AND HOMEAWAY = ?",[2018, 'SHL', 'H'])
lst = c.fetchall()

for i in range(0,len(lst)):

    create_pre_match_analysis(lst[i][0],lst[i][1],lst[i][2],lst[i][3],lst[i][4])
    print(lst[i][4],"loaded")
