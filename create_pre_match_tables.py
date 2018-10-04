#Establish connection to database
import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from functions import get_short_team_name

def create_pre_match_table(gamedate, serie, team, opponent, homeaway):

    print(team)

    output = []

    output.append(gamedate)

    seasonYear = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        seasonYear += 1

    # Get last 5 games

    c.execute("SELECT GAMEID FROM teamgames where seasonid = ? and serie = ? and GAMEDATE < ? and TEAM = ? ORDER BY GAMEDATE DESC LIMIT 5", [seasonYear, serie, gamedate, team])
    games5 = c.fetchall()
    g5 = games5[len(games5)-1][0]
    g1 = games5[0][0]

    output.append(seasonYear)
    output.append(serie)
    output.append(team)

    team_short = get_short_team_name(team)
    output.append(team_short)

    output.append(opponent)

    opp_short = get_short_team_name(opponent)

    output.append(opp_short)

    output.append(homeaway)


    c.execute("""SELECT COUNT(GAMEID) as n_games,
                    SUM(CASE WHEN OUTCOME = 1 THEN 1 else 0 end) as WINS,
                    SUM(CASE WHEN OUTCOME = 2 THEN 1 else 0 end) as OTWINS,
                    SUM(CASE WHEN OUTCOME = 3 THEN 1 else 0 end) as OTLOSSES,
                    SUM(CASE WHEN OUTCOME = 4 THEN 1 else 0 end) as LOSSES,
                    SUM(SCORE1) as SCORED,
                    SUM(SCORE2) as CONCEDED,
                    SUM(SCORE11) as SCORED11,
                    SUM(SCORE12) as SCORED12,
                    SUM(SCORE13) as SCORED13,
                    SUM(SCORE21) as SCORED21,
                    SUM(SCORE22) as SCORED22,
                    SUM(SCORE23) as SCORED23,
                    SUM(PENALTY1) as PENALTY,
                    SUM(PENALTY2) as PENALTY_AGAINST,
                    SUM(SHOTS1) as SHOTS,
                    SUM(SHOTS2) as SHOTS_AGAINST
                FROM
                    TEAMGAMES
                WHERE
                    TEAM = ? and
                    GAMEDATE < ? and
                    SEASONID = ?""", [team, gamedate, seasonYear])

    full_data = c.fetchall()

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

    print(full_data)
    print(home_data)
    print(away_data)
    print(last_five_data)
    print(last_match_data)



    #                SUM(CASE WHEN OUTCOME = 1 and HOMEAWAY = 'A' THEN 1 else 0 end) as HWINS,
#                SUM(CASE WHEN OUTCOME = 2 and HOMEAWAY = 'A' THEN 1 else 0 end) as HOTWINS,
#                SUM(CASE WHEN OUTCOME = 3 and HOMEAWAY = 'A' THEN 1 else 0 end) as HOTLOSSES,
#                SUM(CASE WHEN OUTCOME = 4 and HOMEAWAY = 'A' THEN 1 else 0 end) as HLOSSES,
#
#                """)



#    print(output)