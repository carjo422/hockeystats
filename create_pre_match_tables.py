#Establish connection to database
import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from functions import get_short_team_name
from functions import transform_date
from functions import date_diff
from calcFunctions import calculate_team_strength

def create_pre_match_table(gamedate, serie, team, opponent, homeaway):

    print(team)

    base_table = []
    full_table = []
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

    c.execute("SELECT GAMEDATE, OPPONENT, OUTCOME, SCORE1, SCORE2, OPP_SCORE_SIMPLE FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC",[seasonYear,team, gamedate])

    schedule = c.fetchall()

    sched = 0
    comp1 = 0
    comp2 = 0
    comp3 = 0
    comp4 = 0
    comp5 = 0

    comp1 = schedule[0][5]

    dlast1 = 0
    dlast2 = 0
    dlast3 = 0
    dlast4 = 0
    dlast5 = 0

    if len(schedule) > 0:
        dlast1 = date_diff(gamedate,schedule[0][0])
        comp1 = schedule[0][5]
    if len(schedule) > 1:
        dlast2 = date_diff(gamedate,schedule[1][0])
        comp2 = comp1 + schedule[1][5]
    if len(schedule) > 2:
        dlast3 = date_diff(gamedate,schedule[2][0])
        comp3 = comp2 + schedule[2][5]
    if len(schedule) > 3:
        dlast4 = date_diff(gamedate,schedule[3][0])
        comp4 = comp3 + schedule[3][5]
    if len(schedule) > 4:
        dlast5 = date_diff(gamedate,schedule[4][0])
        comp5 = comp4 + schedule[4][5]

    for i in range(0,len(schedule)):
        sched += 1/date_diff(gamedate,schedule[i][0])

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

    #SCORE DATA

    [score1, form_score1, last_seasons_score1, player_score1] = calculate_team_strength(team, gamedate, c)

    score_data.append(score1)
    score_data.append(form_score1)
    score_data.append(last_seasons_score1)
    score_data.append(player_score1)



    print(base_table)
    print(full_data)
    print(home_data)
    print(away_data)
    print(last_five_data)
    print(last_match_data)
    print(streak_table)
    print(schedule_data)
    print(score_data)



    #                SUM(CASE WHEN OUTCOME = 1 and HOMEAWAY = 'A' THEN 1 else 0 end) as HWINS,
#                SUM(CASE WHEN OUTCOME = 2 and HOMEAWAY = 'A' THEN 1 else 0 end) as HOTWINS,
#                SUM(CASE WHEN OUTCOME = 3 and HOMEAWAY = 'A' THEN 1 else 0 end) as HOTLOSSES,
#                SUM(CASE WHEN OUTCOME = 4 and HOMEAWAY = 'A' THEN 1 else 0 end) as HLOSSES,
#
#                """)



#    print(output)