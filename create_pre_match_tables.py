from functions import get_short_team_name
from functions import transform_date
from functions import date_diff
from calcFunctions import calculate_team_strength
import pandas as pd
import numpy as np

def create_pre_match_table(gamedate, serie, team, homeaway, c, conn):

    #print(team)

    base_table = []
    full_data = []
    home_data = []
    away_data = []
    last_five_data = []
    last_match_data = []
    streak_table = []
    score_data = []

    #BASE TABLE

    base_table.append(gamedate)

    seasonYear = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        seasonYear += 1

    base_table.append(seasonYear)
    base_table.append(serie)
    base_table.append(team)

    team_short = get_short_team_name(team)
    base_table.append(team_short)

    base_table.append(homeaway)

    # Get last 5 games

    c.execute("SELECT GAMEID FROM teamgames where seasonid = ? and serie = ? and GAMEDATE < ? and TEAM = ? ORDER BY GAMEDATE DESC LIMIT 5",[seasonYear, serie, gamedate, team])
    games5 = c.fetchall()

    if len(games5) > 0:

        g5 = games5[len(games5) - 1][0]
        g1 = games5[0][0]

        #FULL SEASON DATA

        c.execute("""SELECT COUNT(GAMEID) as n_games,
                        SUM(CASE WHEN OUTCOME = 1 THEN 1 else 0 end) as WINS,
                        SUM(CASE WHEN OUTCOME = 2 THEN 1 else 0 end) as OTWINS,
                        SUM(CASE WHEN OUTCOME = 3 THEN 1 else 0 end) as OTLOSSES,
                        SUM(CASE WHEN OUTCOME = 4 THEN 1 else 0 end) as LOSSES,
                        SUM(SCORE1) as SCORED,
                        SUM(SCORE2) as CONCEDED,
                        SUM(PENALTY1) as PENALTY,
                        SUM(PENALTY2) as PENALTY_AGAINST,
                        SUM(SHOTS1) as SHOTS,
                        SUM(SHOTS2) as SHOTS_AGAINST,
                        SUM(SCORE11) as SCORED11,
                        SUM(SCORE12) as SCORED12,
                        SUM(SCORE13) as SCORED13,
                        SUM(SCORE21) as SCORED21,
                        SUM(SCORE22) as SCORED22,
                        SUM(SCORE23) as SCORED23
                    FROM
                        TEAMGAMES
                    WHERE
                        TEAM = ? and
                        GAMEDATE < ? and
                        SEASONID = ?""", [team, gamedate, seasonYear])

        full_data = c.fetchall()

        #HOME GAMES DATA

        c.execute("""SELECT COUNT(GAMEID) as n_games,
                        SUM(CASE WHEN OUTCOME = 1 THEN 1 else 0 end) as WINS,
                        SUM(CASE WHEN OUTCOME = 2 THEN 1 else 0 end) as OTWINS,
                        SUM(CASE WHEN OUTCOME = 3 THEN 1 else 0 end) as OTLOSSES,
                        SUM(CASE WHEN OUTCOME = 4 THEN 1 else 0 end) as LOSSES,
                        SUM(SCORE1) as SCORED,
                        SUM(SCORE2) as CONCEDED,
                        SUM(PENALTY1) as PENALTY,
                        SUM(PENALTY2) as PENALTY_AGAINST,
                        SUM(SHOTS1) as SHOTS,
                        SUM(SHOTS2) as SHOTS_AGAINST
                    FROM
                        TEAMGAMES
                    WHERE
                        TEAM = ? and
                        GAMEDATE < ? and
                        SEASONID = ? and
                        HOMEAWAY = ?""", [team, gamedate, seasonYear, 'H'])

        home_data = c.fetchall()

        #AWAY GAMES DATA

        c.execute("""SELECT COUNT(GAMEID) as n_games,
                        SUM(CASE WHEN OUTCOME = 1 THEN 1 else 0 end) as WINS,
                        SUM(CASE WHEN OUTCOME = 2 THEN 1 else 0 end) as OTWINS,
                        SUM(CASE WHEN OUTCOME = 3 THEN 1 else 0 end) as OTLOSSES,
                        SUM(CASE WHEN OUTCOME = 4 THEN 1 else 0 end) as LOSSES,
                        SUM(SCORE1) as SCORED,
                        SUM(SCORE2) as CONCEDED,
                        SUM(PENALTY1) as PENALTY,
                        SUM(PENALTY2) as PENALTY_AGAINST,
                        SUM(SHOTS1) as SHOTS,
                        SUM(SHOTS2) as SHOTS_AGAINST
                    FROM
                        TEAMGAMES
                    WHERE
                        TEAM = ? and
                        GAMEDATE < ? and
                        SEASONID = ? and
                        HOMEAWAY = ?""", [team, gamedate, seasonYear, 'A'])

        away_data = c.fetchall()

        #LAST FIVE DATA

        c.execute("""SELECT COUNT(GAMEID) as n_games,
                        SUM(CASE WHEN OUTCOME = 1 THEN 1 else 0 end) as WINS,
                        SUM(CASE WHEN OUTCOME = 2 THEN 1 else 0 end) as OTWINS,
                        SUM(CASE WHEN OUTCOME = 3 THEN 1 else 0 end) as OTLOSSES,
                        SUM(CASE WHEN OUTCOME = 4 THEN 1 else 0 end) as LOSSES,
                        SUM(SCORE1) as SCORED,
                        SUM(SCORE2) as CONCEDED,
                        SUM(PENALTY1) as PENALTY,
                        SUM(PENALTY2) as PENALTY_AGAINST,
                        SUM(SHOTS1) as SHOTS,
                        SUM(SHOTS2) as SHOTS_AGAINST
                    FROM
                        TEAMGAMES
                    WHERE
                        TEAM = ? and
                        GAMEDATE < ? and
                        SEASONID = ? and
                        GAMEID >= ?""", [team, gamedate, seasonYear, g5])

        last_five_data = c.fetchall()

        #LAST GAME DATA

        c.execute("""SELECT COUNT(GAMEID) as n_games,
                        SUM(CASE WHEN OUTCOME = 1 THEN 1 else 0 end) as WINS,
                        SUM(CASE WHEN OUTCOME = 2 THEN 1 else 0 end) as OTWINS,
                        SUM(CASE WHEN OUTCOME = 3 THEN 1 else 0 end) as OTLOSSES,
                        SUM(CASE WHEN OUTCOME = 4 THEN 1 else 0 end) as LOSSES,
                        SUM(SCORE1) as SCORED,
                        SUM(SCORE2) as CONCEDED,
                        SUM(PENALTY1) as PENALTY,
                        SUM(PENALTY2) as PENALTY_AGAINST,
                        SUM(SHOTS1) as SHOTS,
                        SUM(SHOTS2) as SHOTS_AGAINST
                    FROM
                        TEAMGAMES
                    WHERE
                        TEAM = ? and
                        SEASONID = ? and
                        GAMEID = ?""", [team, seasonYear, g1])

        last_match_data = c.fetchall()

        #STREAK DATA

        c.execute("SELECT HOMEAWAY, OUTCOME FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? order by gamedate DESC", [seasonYear,team,gamedate])
        outcomelist = c.fetchall()
        c.execute("SELECT HOMEAWAY, OUTCOME FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? AND HOMEAWAY = ? order by gamedate DESC",[seasonYear, team,gamedate,'H'])
        h_outcomelist = c.fetchall()
        c.execute("SELECT HOMEAWAY, OUTCOME FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? AND HOMEAWAY = ? order by gamedate DESC",[seasonYear, team,gamedate,'A'])
        a_outcomelist = c.fetchall()

        streak1 = 0
        streak12 = 0
        streak4 = 0
        streak34 = 0

        hstreak1 = 0
        hstreak12 = 0
        hstreak4 = 0
        hstreak34 = 0

        astreak1 = 0
        astreak12 = 0
        astreak4 = 0
        astreak34 = 0

        i = 0
        while i < len(outcomelist) and outcomelist[i][1] in ['1']:
            streak1 += 1
            i += 1

        i = 0
        while i < len(outcomelist) and outcomelist[i][1] in ['1', '2']:
            streak12 += 1
            i += 1

        i = 0
        while i < len(outcomelist) and outcomelist[i][1] in ['4']:
            streak4 += 1
            i += 1

        i = 0
        while i < len(outcomelist) and outcomelist[i][1] in ['3', '4']:
            streak34 += 1
            i += 1

        i = 0
        while i < len(h_outcomelist) and h_outcomelist[i][1] in ['1']:
            hstreak1 += 1
            i += 1

        i = 0
        while i < len(h_outcomelist) and h_outcomelist[i][1] in ['1', '2']:
            hstreak12 += 1
            i += 1

        i = 0
        while i < len(h_outcomelist) and h_outcomelist[i][1] in ['4']:
            hstreak4 += 1
            i += 1

        i = 0
        while i < len(h_outcomelist) and h_outcomelist[i][1] in ['3', '4']:
            hstreak34 += 1
            i += 1

        i = 0
        while i < len(a_outcomelist) and a_outcomelist[i][1] in ['1']:
            astreak1 += 1
            i += 1

        i = 0
        while i < len(a_outcomelist) and a_outcomelist[i][1] in ['1', '2']:
            astreak12 += 1
            i += 1

        i = 0
        while i < len(a_outcomelist) and a_outcomelist[i][1] in ['4']:
            astreak4 += 1
            i += 1

        i = 0
        while i < len(a_outcomelist) and a_outcomelist[i][1] in ['3', '4']:
            astreak34 += 1
            i += 1

        streak_table.append(streak1)
        streak_table.append(streak12)
        streak_table.append(streak4)
        streak_table.append(streak34)
        streak_table.append(hstreak1)
        streak_table.append(hstreak12)
        streak_table.append(hstreak4)
        streak_table.append(hstreak34)
        streak_table.append(astreak1)
        streak_table.append(astreak12)
        streak_table.append(astreak4)
        streak_table.append(astreak34)


    #SCORE DATA

    [score1, form_score1, last_seasons_score1, player_score1] = calculate_team_strength(team, gamedate, c)

    score_data.append(score1)
    score_data.append(form_score1)
    score_data.append(last_seasons_score1)
    score_data.append(player_score1)


    return [base_table, full_data, home_data, away_data, last_five_data, last_match_data, streak_table, score_data]



def get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_table1, score_table2, serie, c, conn, gameid, gamedate, season):

    c.execute("SELECT SUM(SCORE11+SCORE12+SCORE13)*1000/SUM(SHOTS11+SHOTS12+SHOTS13) AS HOME_SHOT_PERCENT, SUM(SHOTS11+SHOTS12+SHOTS13)*10/COUNT(GAMEID) AS HOME_SHOTS FROM (SELECT * FROM TEAMGAMES WHERE SERIE = ? and GAMEDATE < ? and HOMEAWAY = ? ORDER BY GAMEDATE DESC LIMIT 80)",[serie,gamedate,"H"])
    home_s = c.fetchall()

    c.execute("SELECT SUM(SCORE11+SCORE12+SCORE13)*1000/SUM(SHOTS11+SHOTS12+SHOTS13) AS HOME_SHOT_PERCENT, SUM(SHOTS11+SHOTS12+SHOTS13)*10/COUNT(GAMEID) AS HOME_SHOTS FROM (SELECT * FROM TEAMGAMES WHERE SERIE = ? and GAMEDATE < ? and HOMEAWAY = ? ORDER BY GAMEDATE DESC LIMIT 80)",[serie,gamedate,"A"])
    away_s = c.fetchall()

    if home_s[0][0] == None or away_s[0][0] == None:
        c.execute("SELECT SUM(SCORE11+SCORE12+SCORE13)*1000/SUM(SHOTS11+SHOTS12+SHOTS13) AS HOME_SHOT_PERCENT, SUM(SHOTS11+SHOTS12+SHOTS13)*10/COUNT(GAMEID) AS HOME_SHOTS FROM (SELECT * FROM TEAMGAMES WHERE SERIE = ? and HOMEAWAY = ? ORDER BY GAMEDATE ASC LIMIT 80)",[serie, "H"])
        home_s = c.fetchall()

        c.execute("SELECT SUM(SCORE11+SCORE12+SCORE13)*1000/SUM(SHOTS11+SHOTS12+SHOTS13) AS HOME_SHOT_PERCENT, SUM(SHOTS11+SHOTS12+SHOTS13)*10/COUNT(GAMEID) AS HOME_SHOTS FROM (SELECT * FROM TEAMGAMES WHERE SERIE = ? and HOMEAWAY = ? ORDER BY GAMEDATE ASC LIMIT 80)",[serie, "A"])
        away_s = c.fetchall()

    #Expected shots more long term
    average_home_shots_total = home_s[0][1]/10+score_table1[0]-3.1
    average_home_shots_against_total = away_s[0][1]/10 - score_table1[0] + 3.1
    average_away_shots_total = away_s[0][1]/10+score_table2[0]-3.1
    average_away_shots_against_total = home_s[0][1]/10 - score_table2[0] + 3.1

    average_home_score_total = home_s[0][0] / 1000 + score_table1[0]/100 - 0.031
    average_home_score_against_total = away_s[0][0] / 1000 - score_table1[0]/100 + 0.031
    average_away_score_total = away_s[0][0] / 1000 + score_table2[0]/100 - 0.031
    average_away_score_against_total = home_s[0][0] / 1000 - score_table2[0]/100 + 0.031

    #Average goal per shot
    c.execute("SELECT SUM(SCORE11+SCORE12+SCORE13+SCORE21+SCORE22+SCORE23), SUM(SHOTS11+SHOTS12+SHOTS13+SHOTS21+SHOTS22+SHOTS23) FROM (SELECT * FROM TEAMGAMES WHERE GAMEDATE < ? AND SERIE = ? ORDER BY GAMEDATE DESC LIMIT 60)", [gamedate,serie])
    aveg = c.fetchall()

    if len(aveg) == 0 or aveg[0][0] == None:
        average_goal_percent = 0.09
    else:
        average_goal_percent = aveg[0][0]/aveg[0][1]


    if len(home_data1) > 0 and home_data1[0][0] > 0:

        #Basic calculation shots and efficiency

        ave_home_shots = home_data1[0][9] / home_data1[0][0]
        ave_home_shots_against = home_data1[0][10] / home_data1[0][0]

        ave_score_shot_home = home_data1[0][5] / home_data1[0][9]
        ave_conceded_shot_home = home_data1[0][6] / home_data1[0][10]

        # Adjust short term variation on shots

        if home_data1[0][0] < 5:
            ave_home_shots = (ave_home_shots)*(home_data1[0][0]*0.2)+(average_home_shots_total)*(1-home_data1[0][0]*0.2)
            ave_home_shots_against = (ave_home_shots_against) * (home_data1[0][0] * 0.2) + (average_home_shots_against_total) * (1 - home_data1[0][0] * 0.2)

        # Adjust short term variation on efficiency

        if home_data1[0][0] < 10:
            ave_score_shot_home = (ave_score_shot_home)*(home_data1[0][0]*0.1)+(average_home_score_total)*(1-home_data1[0][0]*0.1)
            ave_conceded_shot_home = (ave_conceded_shot_home) * (home_data1[0][0] * 0.1) + (average_home_score_against_total) * (1 - home_data1[0][0] * 0.1)

    else:

        # If no matches yet

        ave_home_shots = average_home_shots_total
        ave_home_shots_against = average_home_shots_against_total

        ave_score_shot_home = average_home_score_total
        ave_conceded_shot_home = average_home_score_against_total


    if len(away_data2) > 0 and away_data2[0][0] > 0:

        # Basic calculation shots and efficiency

        ave_away_shots = away_data2[0][9] / away_data2[0][0]
        ave_away_shots_against = away_data2[0][10] / away_data2[0][0]

        ave_score_shot_away = away_data2[0][5] / away_data2[0][9]
        ave_conceded_shot_away = away_data2[0][6] / away_data2[0][10]

        #Adjust short term variation on shots

        if away_data2[0][0] < 10:
            ave_away_shots = (ave_away_shots) * (away_data2[0][0] * 0.1) + (average_away_shots_total) * (1 - away_data2[0][0] * 0.1)
            ave_away_shots_against = (ave_away_shots_against) * (away_data2[0][0] * 0.1) + (average_away_shots_against_total) * ( 1 - away_data2[0][0] * 0.1)

        # Adjust short term variation on efficiency

        if away_data2[0][0] < 10:
            ave_score_shot_away = (ave_score_shot_away) * (away_data2[0][0] * 0.1) + (average_away_score_total) * (1 - away_data2[0][0] * 0.1)
            ave_conceded_shot_away = (ave_conceded_shot_away) * (away_data2[0][0] * 0.1) + (average_away_score_against_total) * (1 - away_data2[0][0] * 0.1)


    else:

        # If no matches yet

        ave_away_shots = average_away_shots_total
        ave_away_shots_against = average_away_shots_against_total

        ave_score_shot_away = average_away_score_total
        ave_conceded_shot_away = average_away_score_against_total

    c.execute("SELECT GAMEID, HOMETEAM, AWAYTEAM, (HSHOTS1+HSHOTS2+HSHOTS3) AS SHOTS1, (ASHOTS1+ASHOTS2+ASHOTS3) AS SHOTS2, (HSCORE1+HSCORE2+HSCORE3) AS GOAL1, (ASCORE1+ASCORE2+ASCORE3) AS GOAL2 FROM STATS WHERE GAMEID = ?",[gameid])
    sts = c.fetchall()

    c.execute("SELECT GAMEID FROM EXP_SHOTS_TABLE WHERE GAMEID = ?",[gameid])
    chk = c.fetchall()

    if len(chk) == 0 and len(sts) > 0:
        c.execute("INSERT INTO EXP_SHOTS_TABLE (GAMEID, GAMEDATE, SEASON, SERIE, HOMETEAM, AWAYTEAM, AHS, AHSA, ASSH, ACSH, AAS, AASA, ASSA, ACSA, ACT_SHOTS1, ACT_SHOTS2, ACT_GOALS1, ACT_GOALS2, SCORE1, SCORE2, AGP) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [sts[0][0], gamedate, season, serie, sts[0][1], sts[0][2], ave_home_shots-home_s[0][1]/10, ave_home_shots_against-away_s[0][1]/10, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots-away_s[0][1]/10, ave_away_shots_against-home_s[0][1]/10, ave_score_shot_away, ave_conceded_shot_away, sts[0][3], sts[0][4], sts[0][5], sts[0][6], score_table1[3], score_table2[3], average_goal_percent])
    elif len(sts) > 0:
        c.execute("UPDATE EXP_SHOTS_TABLE SET AHS = ?, AHSA = ?, ASSH = ?, ACSH = ?, AAS = ?, AASA = ?, ASSA = ?, ACSA = ?, ACT_SHOTS1 = ?, ACT_SHOTS2 = ?, ACT_GOALS1 = ?, ACT_GOALS2 = ?, SCORE1 = ?, SCORE2 = ?, AGP = ? WHERE GAMEID = ?",
        [ave_home_shots-home_s[0][1]/10, ave_home_shots_against-away_s[0][1]/10, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots-away_s[0][1]/10, ave_away_shots_against-home_s[0][1]/10, ave_score_shot_away, ave_conceded_shot_away, sts[0][3], sts[0][4], sts[0][5], sts[0][6], score_table1[3], score_table2[3], average_goal_percent, gameid])

    conn.commit()

    return [ave_home_shots-home_s[0][1]/10, ave_home_shots_against-away_s[0][1]/10, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots-away_s[0][1]/10, ave_away_shots_against-home_s[0][1]/10, ave_score_shot_away, ave_conceded_shot_away, average_goal_percent]


def get_ANN_odds(gameid, serie, gamedate, seasonYear, c, conn):

    if gameid != "":

        c.execute("SELECT HOMETEAM, AWAYTEAM, SCORE1, SCORE2, ACT_SHOTS1, ACT_SHOTS2, ACT_GOALS1, ACT_GOALS2 FROM EXP_SHOTS_TABLE WHERE GAMEID = ?",[gameid])
        exp_table_data = c.fetchall()

        c.execute("SELECT GAMEID FROM GOALS_FOREST_TABLE_1 WHERE GAMEID = ?",[gameid])
        chk = c.fetchall()

        if len(exp_table_data) == 0:

            c.execute("SELECT HOMETEAM, AWAYTEAM FROM STATS WHERE GAMEID = ?",[gameid])
            teams = c.fetchall()

            [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1,score_data1] = create_pre_match_table(gamedate, serie, teams[0][0], "H", c, conn)
            [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2,score_data2] = create_pre_match_table(gamedate, serie, teams[0][1], "A", c, conn)

            get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_data1, score_data2,serie, c, conn, gameid, gamedate, seasonYear)

            c.execute("SELECT HOMETEAM, AWAYTEAM, SCORE1, SCORE2, ACT_SHOTS1, ACT_SHOTS2, ACT_GOALS1, ACT_GOALS2 FROM EXP_SHOTS_TABLE WHERE GAMEID = ?",[gameid])
            exp_table_data = c.fetchall()

            conn.commit()

            print(gameid, "added to Exp_Shots_Table")


        score1 = exp_table_data[0][2] ** (1 / 2)
        score2 = exp_table_data[0][3] ** (1 / 2)

        score1d = (25 / exp_table_data[0][2]) ** (1 / 2)
        score2d = (25 / exp_table_data[0][3]) ** (1 / 2)

        act_shots1 = exp_table_data[0][4]
        act_shots2 = exp_table_data[0][5]
        act_goals1 = exp_table_data[0][6]
        act_goals2 = exp_table_data[0][7]

        off_score1 = (act_shots1 + (act_goals1 - act_goals2) * 4) * (score2) / 180
        off_score2 = (act_shots2 + (act_goals2 - act_goals1) * 4) * (score1) / 140

        def_score1 = (act_shots2 + (act_goals2 - act_goals1) * 3) * (score2d) / 100
        def_score2 = (act_shots1 + (act_goals1 - act_goals2) * 3) * (score1d) / 130

        if exp_table_data[0][6] == exp_table_data[0][7]:
            outcome = 1
        elif exp_table_data[0][6] > exp_table_data[0][7]:
            outcome = 0
        elif exp_table_data[0][6] < exp_table_data[0][7]:
            outcome = 2

        if exp_table_data[0][6] + exp_table_data[0][7] < 5:
            out45 = 0
        else:
            out45 = 1

        if len(chk) == 0:
            c.execute("INSERT INTO GOALS_FOREST_TABLE_1 (GAMEID, GAMEDATE, SEASONID, SERIE, HOMETEAM, AWAYTEAM, SCORE1, SCORE2, ACT_SHOTS1, ACT_SHOTS2, ACT_GOALS1, ACT_GOALS2, OFF_SCORE_GAME1, OFF_SCORE_GAME2, DEF_SCORE_GAME1, DEF_SCORE_GAME2, OUTCOME1X2, OUTCOME45) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      [gameid, gamedate, seasonYear, serie, exp_table_data[0][0], exp_table_data[0][1], exp_table_data[0][2], exp_table_data[0][3], exp_table_data[0][4], exp_table_data[0][5], exp_table_data[0][6], exp_table_data[0][7], off_score1, off_score2, def_score1, def_score2, outcome, out45])

        else:
            c.execute("UPDATE GOALS_FOREST_TABLE_1 SET SCORE1 = ?, SCORE2 = ?, OFF_SCORE_GAME1 = ?, OFF_SCORE_GAME2 = ?, DEF_SCORE_GAME1 = ?, DEF_SCORE_GAME2 = ? WHERE GAMEID = ?",[exp_table_data[0][2], exp_table_data[0][3], off_score1, off_score2, def_score1, def_score2, gameid])

        conn.commit()


def update_model1_data(serie, c, conn):

    c.execute("SELECT GAMEDATE, SERIE, TEAM, OPPONENT, GAMEID, SEASONID FROM TEAMGAMES WHERE (SEASONID = ? OR SEASONID = ? OR SEASONID = ?) AND SERIE = ? AND HOMEAWAY = ? ORDER BY GAMEDATE ",[2019, 2018, 2017, serie, 'H'])
    lst = c.fetchall()

    for i in range(0, len(lst)):
        gameid = lst[i][4]
        serie = lst[i][1]
        gamedate = lst[i][0]
        seasonYear = lst[i][5]

        #print(gameid, serie, gamedate, seasonYear)

        get_ANN_odds(gameid, serie, gamedate, seasonYear, c, conn)

        #print(gameid, seasonYear)

        conn.commit()

    for i in range(0, len(lst)):

        gameid = lst[i][4]
        serie = lst[i][1]
        gamedate = lst[i][0]
        seasonYear = lst[i][5]

        c.execute("SELECT SCORE1, SCORE2 FROM EXP_SHOTS_TABLE WHERE GAMEID = ?",[gameid])
        scores = c.fetchall()

        c.execute("SELECT HOMETEAM, COUNT(GAMEID), AVG(SCORE1), AVG(OFF_SCORE_GAME1), AVG(DEF_SCORE_GAME1) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (HOMETEAM = ?) ORDER BY GAMEDATE DESC LIMIT 6)",[gamedate, seasonYear, lst[i][2]])
        hth_data = c.fetchall()
        c.execute("SELECT AWAYTEAM, COUNT(GAMEID), AVG(SCORE2), AVG(OFF_SCORE_GAME2), AVG(DEF_SCORE_GAME2) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (AWAYTEAM = ?) ORDER BY GAMEDATE DESC LIMIT 4)",[gamedate, seasonYear, lst[i][2]])
        hta_data = c.fetchall()

        if (hth_data[0][1] + hta_data[0][1]) > 0 and hth_data[0][0] != None and hta_data[0][0] != None:
            home_team_off = (hth_data[0][1] * hth_data[0][3] + hta_data[0][1] * hta_data[0][3]) / (hth_data[0][1] + hta_data[0][1])
            home_team_def = (hth_data[0][1] * hth_data[0][4] + hta_data[0][1] * hta_data[0][4]) / (hth_data[0][1] + hta_data[0][1])

            home_team_off = home_team_off * (hth_data[0][1] + hta_data[0][1]) / 10 + scores[0][0]/15 * (10-(hth_data[0][1] + hta_data[0][1])) / 10
            home_team_def = home_team_def * (hth_data[0][1] + hta_data[0][1]) / 10 + (1-scores[0][0]/12) * (10-(hth_data[0][1] + hta_data[0][1])) / 10

        else:


            home_team_off = scores[0][0]/15
            home_team_def = 1-scores[0][0]/12



        c.execute("UPDATE GOALS_FOREST_TABLE_1 SET OFF_SCORE_HOME = ?, DEF_SCORE_HOME = ? WHERE GAMEID = ?",[home_team_off, home_team_def, gameid])



        c.execute("SELECT HOMETEAM, COUNT(GAMEID), AVG(SCORE1), AVG(OFF_SCORE_GAME1), AVG(DEF_SCORE_GAME1) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (HOMETEAM = ?) ORDER BY GAMEDATE DESC LIMIT 4)",[gamedate, seasonYear, lst[i][3]])
        hth_data = c.fetchall()
        c.execute("SELECT AWAYTEAM, COUNT(GAMEID), AVG(SCORE2), AVG(OFF_SCORE_GAME2), AVG(DEF_SCORE_GAME2) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (AWAYTEAM = ?) ORDER BY GAMEDATE DESC LIMIT 6)",[gamedate, seasonYear, lst[i][3]])
        hta_data = c.fetchall()

        if (hth_data[0][1] + hta_data[0][1]) > 0 and hth_data[0][0] != None and hta_data[0][0] != None:
            away_team_off = (hth_data[0][1] * hth_data[0][3] + hta_data[0][1] * hta_data[0][3]) / (hth_data[0][1] + hta_data[0][1])
            away_team_def = (hth_data[0][1] * hth_data[0][4] + hta_data[0][1] * hta_data[0][4]) / (hth_data[0][1] + hta_data[0][1])

            away_team_off = away_team_off * (hth_data[0][1] + hta_data[0][1]) / 10 + scores[0][1] / 15 * (10 - (hth_data[0][1] + hta_data[0][1])) / 10
            away_team_def = away_team_def * (hth_data[0][1] + hta_data[0][1]) / 10 + (1 - scores[0][1] / 12) * (10 - (hth_data[0][1] + hta_data[0][1])) / 10

        else:

            away_team_off = scores[0][1] / 15
            away_team_def = 1 - scores[0][1] / 12

        c.execute("UPDATE GOALS_FOREST_TABLE_1 SET OFF_SCORE_AWAY = ?, DEF_SCORE_AWAY = ? WHERE GAMEID = ?",[away_team_off, away_team_def, gameid])

        conn.commit()

def update_model2_data(serie, seasonYear, c, conn):

    c.execute("SELECT GAMEID, GAMEDATE, HOMETEAM, AWAYTEAM FROM STATS WHERE SEASONID < ? AND SERIE = ?", [seasonYear, serie])
    lst = c.fetchall()

    for i in range(0,len(lst)):

        gameid = lst[i][0]
        print(gameid)
        gamedate = lst[i][1]
        hometeam = lst[i][2]
        awayteam = lst[i][3]

        [base_table1, full_data1, home_data1, away_data1, last_five_data1, last_match_data1, streak_table1, score_data1] = create_pre_match_table(gamedate, serie, hometeam, "H", c, conn)
        [base_table2, full_data2, home_data2, away_data2, last_five_data2, last_match_data2, streak_table2, score_data2] = create_pre_match_table(gamedate, serie, awayteam, "A", c, conn)

        score1 = score_data1[3]
        score2 = score_data2[3]

        if serie == 'HA':
            score1 *= 2
            score2 *= 2

        comb_score_home = get_model1_data(score1, full_data1, home_data1, last_five_data1, last_match_data1, "H")
        comb_score_away = get_model2_data(score2, full_data2, away_data2, last_five_data2, last_match_data2, "A")

        c.execute("SELECT HSCORE1+HSCORE2+HSCORE3, ASCORE1+ASCORE2+ASCORE3, HSHOTS1+HSHOTS2+HSHOTS3, ASHOTS1+ASHOTS2+ASHOTS3 FROM STATS WHERE GAMEID = ?",[gameid])
        sts = c.fetchall()

        if sts[0][0] == sts[0][1]:
            outcome = 1
        elif sts[0][0] > sts[0][1]:
            outcome = 0
        else:
            outcome = 2

        if sts[0][0] + sts[0][1] < 5:
            outcome45 = 0
        else:
            outcome45 = 1

        c.execute("SELECT GAMEID FROM GOALS_FOREST_TABLE_2 WHERE GAMEID = ?",[gameid])
        chk = c.fetchall()

        if len(chk) > 0:
            c.execute("UPDATE GOALS_FOREST_TABLE_2 SET SERIE = ?, COMB_SCORE_HOME = ?, COMB_SCORE_AWAY = ? WHERE GAMEID = ?",[serie, comb_score_home, comb_score_away, gameid])
        else:
            c.execute("INSERT INTO GOALS_FOREST_TABLE_2 (GAMEID, GAMEDATE, SEASONID, SERIE, HOMETEAM, AWAYTEAM, SCORE1, SCORE2, COMB_SCORE_HOME, COMB_SCORE_AWAY, ACT_SHOTS1, ACT_SHOTS2, ACT_GOALS1, ACT_GOALS2, OUTCOME1X2, OUTCOME45) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                      ,[gameid, gamedate, seasonYear, serie, hometeam, awayteam, score_data1[3], score_data2[3], comb_score_home, comb_score_away, sts[0][2], sts[0][3], sts[0][0], sts[0][1], outcome, outcome45])

    conn.commit()

def get_model1_data(serie, seasonYear, gamedate, home_team, away_team, c, conn):

    from calcFunctions import calculate_team_strength

    score1 = calculate_team_strength(home_team, gamedate, c)[3]
    score2 = calculate_team_strength(away_team, gamedate, c)[3]

    c.execute("SELECT HOMETEAM, COUNT(GAMEID), AVG(SCORE1), AVG(OFF_SCORE_GAME1), AVG(DEF_SCORE_GAME1) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (HOMETEAM = ?) ORDER BY GAMEDATE DESC LIMIT 6)",[gamedate, seasonYear, home_team])
    hth_data = c.fetchall()
    c.execute("SELECT AWAYTEAM, COUNT(GAMEID), AVG(SCORE2), AVG(OFF_SCORE_GAME2), AVG(DEF_SCORE_GAME2) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (AWAYTEAM = ?) ORDER BY GAMEDATE DESC LIMIT 4)",[gamedate, seasonYear, home_team])
    hta_data = c.fetchall()

    if (hth_data[0][1] + hta_data[0][1]) > 0 and hth_data[0][0] != None and hta_data[0][0] != None:
        home_team_off = (hth_data[0][1] * hth_data[0][3] + hta_data[0][1] * hta_data[0][3]) / (hth_data[0][1] + hta_data[0][1])
        home_team_def = (hth_data[0][1] * hth_data[0][4] + hta_data[0][1] * hta_data[0][4]) / (hth_data[0][1] + hta_data[0][1])

        home_team_off = home_team_off * (hth_data[0][1] + hta_data[0][1]) / 10 + score1 / 15 * (10 - (hth_data[0][1] + hta_data[0][1])) / 10
        home_team_def = home_team_def * (hth_data[0][1] + hta_data[0][1]) / 10 + (1 - score1 / 12) * (10 - (hth_data[0][1] + hta_data[0][1])) / 10

    else:

        home_team_off = score1 / 15
        home_team_def = 1 - score1 / 12



    c.execute("SELECT HOMETEAM, COUNT(GAMEID), AVG(SCORE1), AVG(OFF_SCORE_GAME1), AVG(DEF_SCORE_GAME1) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (HOMETEAM = ?) ORDER BY GAMEDATE DESC LIMIT 4)",[gamedate, seasonYear, away_team])
    hth_data = c.fetchall()
    c.execute("SELECT AWAYTEAM, COUNT(GAMEID), AVG(SCORE2), AVG(OFF_SCORE_GAME2), AVG(DEF_SCORE_GAME2) FROM (SELECT * FROM GOALS_FOREST_TABLE_1 WHERE  GAMEDATE < ? AND SEASONID = ? AND (AWAYTEAM = ?) ORDER BY GAMEDATE DESC LIMIT 6)",[gamedate, seasonYear, away_team])
    hta_data = c.fetchall()

    if (hth_data[0][1] + hta_data[0][1]) > 0 and hth_data[0][0] != None and hta_data[0][0] != None:
        away_team_off = (hth_data[0][1] * hth_data[0][3] + hta_data[0][1] * hta_data[0][3]) / (hth_data[0][1] + hta_data[0][1])
        away_team_def = (hth_data[0][1] * hth_data[0][4] + hta_data[0][1] * hta_data[0][4]) / (hth_data[0][1] + hta_data[0][1])

        away_team_off = away_team_off * (hth_data[0][1] + hta_data[0][1]) / 10 + score2 / 15 * (10 - (hth_data[0][1] + hta_data[0][1])) / 10
        away_team_def = away_team_def * (hth_data[0][1] + hta_data[0][1]) / 10 + (1 - score2 / 12) * (10 - (hth_data[0][1] + hta_data[0][1])) / 10

    else:

        away_team_off = score2 / 15
        away_team_def = 1 - score2 / 12


    return home_team_off, home_team_def, away_team_off, away_team_def


def get_model2_data(score, full_data, ven_data, last_five_data, last_match_data,v):


    total_weight = 0
    output = 0

    #Add score to total

    weight = 10

    value = score / 5 + 0.3
    value = max(min(value,2.25),0.85)

    #print("SCORE VALUE",weight, value)

    total_weight += weight
    output += weight * value

    #Add full data to total
    if len(full_data) > 0:
        if full_data[0][0] > 0:

            weight = min(10, full_data[0][0])

            value = 0
            value += (full_data[0][1]*3 + full_data[0][2]*2 + full_data[0][3]*1)/full_data[0][0]
            value = max(min(value,2.25),0.85)

            total_weight += weight
            output += weight * value

            #print("FULL DATA VALUE", weight, value)

    # Add ven data to total
    if len(ven_data) > 0:
        if ven_data[0][0] > 0:
            weight = min(10, full_data[0][0])

            value = 0
            value += (ven_data[0][1]*3 + ven_data[0][2]*2 + ven_data[0][3]*1)/ven_data[0][0]
            value = max(min(value,2.25),0.85)

            if v == "H":
                value /= 1.3

            total_weight += weight
            output += weight * value

            #print("VEN DATA VALUE", weight, value)

    # Add last 5 data to total
    if len(last_five_data) > 0:
        if last_five_data[0][0] > 0:
            weight = min(20, full_data[0][0])

            value = 0
            value += (last_five_data[0][1] * 3 + last_five_data[0][2] * 2 + last_five_data[0][3] * 1) / last_five_data[0][0]
            value = max(min(value, 2.25), 0.85)

            total_weight += weight
            output += weight * value

            #print("LAST FIVE VALUE", weight, value)

    output = output / total_weight


    return output







