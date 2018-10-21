#Establish connection to database
import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from functions import get_short_team_name
from functions import transform_date
from functions import date_diff
from calcFunctions import calculate_team_strength

def create_pre_match_table(gamedate, serie, team, homeaway):

    #print(team)

    base_table = []
    full_data = []
    home_data = []
    away_data = []
    last_five_data = []
    last_match_data = []
    streak_table = []
    schedule_data = []
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

        #SCHEDULE DATA

        c.execute("SELECT GAMEDATE, OPPONENT, OUTCOME, SCORE1, SCORE2, OPP_SCORE_SIMPLE, CASE WHEN HOMEAWAY = ? then 0.95 else 1.1 end as HAFACT FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC",['H',seasonYear,team, gamedate])
        schedule = c.fetchall()

        c.execute("SELECT GAMEDATE FROM CHL_GAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ?", [seasonYear, team, gamedate])
        CHLschedule = c.fetchall()

        sched = 0
        comp1 = 0
        comp2 = 0
        comp3 = 0
        comp4 = 0
        comp5 = 0

        dlast1 = 0
        dlast2 = 0
        dlast3 = 0
        dlast4 = 0
        dlast5 = 0

        out1 = 0
        out2 = 0
        out3 = 0
        out4 = 0
        out5 = 0

        [ha1,ha2,ha3,ha4,ha5] = [0,0,0,0,0]

        if len(schedule) > 0:
            dlast1 = date_diff(gamedate,schedule[0][0])
            comp1 = schedule[0][5]
            out1 = int(schedule[0][2])
            ha1 = schedule[0][6]
        if len(schedule) > 1:
            dlast2 = date_diff(gamedate,schedule[1][0])
            comp2 = comp1 + schedule[1][5]
            out2 = int(schedule[1][2])
            ha2 = schedule[1][6]
        if len(schedule) > 2:
            dlast3 = date_diff(gamedate,schedule[2][0])
            comp3 = comp2 + schedule[2][5]
            out3 = int(schedule[2][2])
            ha3 = schedule[2][6]
        if len(schedule) > 3:
            dlast4 = date_diff(gamedate,schedule[3][0])
            comp4 = comp3 + schedule[3][5]
            out4 = int(schedule[3][2])
            ha4 = schedule[3][6]
        if len(schedule) > 4:
            dlast5 = date_diff(gamedate,schedule[4][0])
            comp5 = comp4 + schedule[4][5]
            out5 = int(schedule[4][2])
            ha5 = schedule[4][6]

        for i in range(0,len(schedule)):

            if date_diff(gamedate,schedule[i][0]) < 13:
                sched += 1/date_diff(gamedate,schedule[i][0])

        for i in range(0,len(CHLschedule)):
            if date_diff(gamedate, CHLschedule[i][0]) < 13:
                sched += 1/date_diff(gamedate,CHLschedule[i][0])


        schedule_data.append(sched)
        schedule_data.append(comp1)
        schedule_data.append(comp2)
        schedule_data.append(comp3)
        schedule_data.append(comp4)
        schedule_data.append(comp5)
        schedule_data.append(dlast1)
        schedule_data.append(dlast2)
        schedule_data.append(dlast3)
        schedule_data.append(dlast4)
        schedule_data.append(dlast5)

        formcorp = 0
        formweight = 0


        if out1 > 0:
            compadd = max(comp1-3,0)
            formcorp += (((4-out1)*(comp1))**(1/2)+compadd)*1*ha1
            formweight += 1

        if out2 > 0:
            compadd = max(comp2 - 3, 0)
            formcorp += (((4 - out2) * (comp2)) ** (1 / 2) + compadd) * 0.8*ha2
            formweight += 0.8

        if out3 > 0:
            compadd = max(comp3 - 3, 0)
            formcorp += (((4 - out3) * (comp3)) ** (1 / 2) + compadd) * 0.6*ha3
            formweight += 0.6

        if out4 > 0:
            compadd = max(comp4 - 3, 0)
            formcorp += (((4 - out4) * (comp4)) ** (1 / 2) + compadd) * 0.5*ha4
            formweight += 0.5

        if out5 > 0:
            compadd = max(comp5 - 3, 0)
            formcorp += (((4 - out5) * (comp5)) ** (1 / 2) + compadd) * 0.4*ha5
            formweight += 0.4

        if formweight == 0:
            formcorp = 2
        else:
            formcorp /= formweight


        schedule_data.append(formcorp)

    #SCORE DATA

    [score1, form_score1, last_seasons_score1, player_score1] = calculate_team_strength(team, gamedate, c)

    score_data.append(score1)
    score_data.append(form_score1)
    score_data.append(last_seasons_score1)
    score_data.append(player_score1)



    #print(base_table)
    #print(full_data)
    #print(home_data)
    #print(away_data)
    #print(last_five_data)
    #print(last_match_data)
    #print(streak_table)
    #print(schedule_data)
    #print(score_data)

    return [base_table, full_data, home_data, away_data, last_five_data, last_match_data, streak_table, schedule_data, score_data]


def create_pre_match_players(gamedate, serie, team, homeaway):
    pass

    # GOALS
    # PPGOALS
    # SHGOALS
    # ASSISTS
    # PLUS
    # MINUS
    # PENALTY
    # SHOTSAT
    # SAVES
    # SCORE

def get_expected_shots(full_data1, home_data1, away_data2, full_data2, home_data2, score_table1, score_table2, serie, c, gameid, gamedate, season):

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
        c.execute("INSERT INTO EXP_SHOTS_TABLE (GAMEID, GAMEDATE, SEASON, SERIE, HOMETEAM, AWAYTEAM, AHS, AHSA, ASSH, ACSH, AAS, AASA, ASSA, ACSA, ACT_SHOTS1, ACT_SHOTS2, ACT_GOAL1, ACT_GOAL2, SCORE1, SCORE2) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [sts[0][0], gamedate, season, serie, sts[0][1], sts[0][2], ave_home_shots-home_s[0][1]/10, ave_home_shots_against-away_s[0][1]/10, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots-away_s[0][1]/10, ave_away_shots_against-home_s[0][1]/10, ave_score_shot_away, ave_conceded_shot_away, sts[0][3], sts[0][4], sts[0][5], sts[0][6], score_table1[0],score_table2[0]])
    elif len(sts) > 0:
        c.execute("UPDATE EXP_SHOTS_TABLE SET AHS = ?, AHSA = ?, ASSH = ?, ACSH = ?, AAS = ?, AASA = ?, ASSA = ?, ACSA = ?, ACT_SHOTS1 = ?, ACT_SHOTS2 = ?, ACT_GOAL1 = ?, ACT_GOAL2 = ?, SCORE1 = ?, SCORE2 = ? WHERE GAMEID = ?",
        [ave_home_shots-home_s[0][1]/10, ave_home_shots_against-away_s[0][1]/10, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots-away_s[0][1]/10, ave_away_shots_against-home_s[0][1]/10, ave_score_shot_away, ave_conceded_shot_away, sts[0][3], sts[0][4], sts[0][5], sts[0][6], score_table1[0],score_table2[0],gameid])

    return [ave_home_shots-home_s[0][1]/10, ave_home_shots_against-away_s[0][1]/10, ave_score_shot_home, ave_conceded_shot_home, ave_away_shots-away_s[0][1]/10, ave_away_shots_against-home_s[0][1]/10, ave_score_shot_away, ave_conceded_shot_away]



