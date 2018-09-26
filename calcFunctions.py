import numpy as np
import datetime
import calendar
import sqlite3

from functions import mean_list

def create_game_rating(lineup,c,team):

    output = []

    #Get some additional information from stats

    c.execute("SELECT * FROM stats where gameid = ?",[lineup[0][1]])
    stats = c.fetchall()

    #print(stats)
    if team == stats[0][4]:
        opponent = stats[0][5]
        homeaway = 1
        score1 = stats[0][6]
        score2 = stats[0][7]
        shots1 = stats[0][8]
        shots2 = stats[0][9]
    else:
        opponent = stats[0][4]
        homeaway = 2
        score1 = stats[0][7]
        score2 = stats[0][6]
        shots1 = stats[0][9]
        shots2 = stats[0][8]

    for i in range(0,len(lineup)):

        # Some variables
        gamedate = lineup[i][9]
        seasonid = lineup[i][2]
        gameid = lineup[i][1]

    # Get player line

        if lineup[i][13] == 'Goalies':
            line = 0
        elif lineup[i][13] == '1st Line':
            line = 1
        elif lineup[i][13] == '2nd Line':
            line = 2
        elif lineup[i][13] == '3rd Line':
            line = 3
        elif lineup[i][13] == '4th Line':
            line = 4
        else:
            line = 5

    # Get player position

        c.execute("SELECT position from rosters where SEASONID = ? and TEAM = ? and SERIE = ? and NUMBER = ?",[lineup[i][2],team,lineup[i][3],lineup[i][10]])
        position = c.fetchall()

        if len(position) > 0:
            position = position[0][0]
        else:
            position = ""

    # Get lineup information

        currentserie = lineup[i][3]
        goals = lineup[i][16]
        PPgoals = lineup[i][17]
        SHgoals = lineup[i][18]
        assist = lineup[i][19]
        plus = lineup[i][20]
        minus = lineup[i][21]
        penalty = lineup[i][22]
        inPP = lineup[i][23]
        inBP = lineup[i][24]
        shots = lineup[i][25]
        saves = lineup[i][26]

        if lineup[i][6] == lineup[i][8]:
            comp = lineup[i][7]
        else:
            comp = lineup[i][6]

    # How good is the competition

        compstat = calculate_team_strength(comp,gamedate)

        olddate = stats[0][3]
        c.execute("SELECT SEASONID, SERIE, SUM(CASE WHEN OUTCOME = 1 THEN 3 WHEN OUTCOME = 2 THEN 2 WHEN OUTCOME = 3 THEN 1 ELSE 0 END) POINTS, COUNT(TEAM) as MATCHES FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? AND GAMEDATE < ? AND GAMEDATE >= ? GROUP BY SEASONID, SERIE", [opponent, stats[0][0], stats[0][3], olddate])
        form = c.fetchall()

        score = 0
        offScore = 0
        defScore = 0

        if "D" in position:

            score += goals * 12 + PPgoals * 6 + SHgoals * 12 + assist * 6 + plus * 5 + minus * -8 + inPP * 5 + inBP * 5 - penalty * 4

            if minus == 0:
                if line == 1:
                    score += 10
                elif line == 2:
                    score += 6
                elif line in [3,4]:
                    score +=3
                else:
                    score +=1

            score += (shots * 2.6 + (shots - saves) * -20)/6

        elif position == "GK":

            score += assist * 10
            score += plus * 5
            score += minus *-5
            score += shots*2.6 + (shots-saves)*-20
            score -= penalty * 10

        else:

            score += goals * 12 + PPgoals * 6 + SHgoals * 12 + assist * 8 + plus * 6 + minus * -7 + inPP * 5 + inBP * 5 - penalty * 6

            if minus == 0:
                if line == 1:
                    score += 6
                elif line == 2:
                    score += 2

            score += (shots * 2.6 + (shots - saves) * -20) / 15


        score *= ((compstat)/2+0.5)


        if homeaway == 2:
            score += 5

        if score < -10:
            finalScore = 1
        elif score >= -10 and score < 10:
            finalScore = 2
        elif score >= 10 and score < 25:
            finalScore = 3
        elif score >= 25 and score < 50:
            finalScore = 4
        elif score >= 50:
            finalScore = 5

    offScore = finalScore #For later development
    defScore = finalScore #For later development

    playerScore = [score, finalScore, offScore, defScore]

    return playerScore



def create_teamgames(seasonYear, serie):
#Team games table

    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()

    c.execute("SELECT * FROM stats WHERE SEASONID = ? and SERIE = ?",[seasonYear,serie])
    statsgames = c.fetchall()

    for i in range(0, len(statsgames)):
        c.execute(
            "SELECT GAMEID as GAMEID FROM TEAMGAMES where GAMEID = ? and TEAM = ?",
            [statsgames[i][2],statsgames[i][4]])
        hits = c.fetchall()

        if len(hits) == 0:

            outcome = 0

            if statsgames[i][14]+statsgames[i][15]+statsgames[i][16] > statsgames[i][18]+statsgames[i][19]+statsgames[i][20]:
                outcome = 1
            elif statsgames[i][14]+statsgames[i][15]+statsgames[i][16] < statsgames[i][18]+statsgames[i][19]+statsgames[i][20]:
                outcome = 4
            else:
                if statsgames[i][6] > statsgames[i][7]:
                    outcome = 2
                else:
                    outcome = 3

            c.execute("""INSERT INTO
                            TEAMGAMES (
                               SEASONID,SERIE,GAMEID,GAMEDATE,TEAM,HOMEAWAY,OPPONENT,OUTCOME,SCORE1,SCORE2,SHOTS1,SHOTS2,SAVES1,SAVES2,PENALTY1,PENALTY2,SCORE11,SCORE12,SCORE13,SCORE14,SCORE21,SCORE22,SCORE23,SCORE24,SHOTS11,SHOTS12,SHOTS13,SHOTS14,SHOTS21,SHOTS22,SHOTS23,SHOTS24)
                            VALUES
                                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (statsgames[i][0], statsgames[i][1],statsgames[i][2],statsgames[i][3],statsgames[i][4],'H',statsgames[i][5],outcome,statsgames[i][6],statsgames[i][7],statsgames[i][8],statsgames[i][9],statsgames[i][10],statsgames[i][11],statsgames[i][12],statsgames[i][13],statsgames[i][14],statsgames[i][15],statsgames[i][16],statsgames[i][17],
                       statsgames[i][18], statsgames[i][19], statsgames[i][20], statsgames[i][21], statsgames[i][22], statsgames[i][23],statsgames[i][24], statsgames[i][25],statsgames[i][26], statsgames[i][27], statsgames[i][28], statsgames[i][29]

                       ))

        else:
            pass

        c.execute(
            "SELECT GAMEID as GAMEID FROM TEAMGAMES where GAMEID = ? and TEAM = ?",
            [statsgames[i][2], statsgames[i][5]])
        hits = c.fetchall()

        if len(hits) == 0:

            outcome = 0

            if statsgames[i][14] + statsgames[i][15] + statsgames[i][16] < statsgames[i][18] + statsgames[i][19] + statsgames[i][20]:
                outcome = 1
            elif statsgames[i][14] + statsgames[i][15] + statsgames[i][16] > statsgames[i][18] + statsgames[i][19] + statsgames[i][20]:
                outcome = 4
            else:
                if statsgames[i][6] < statsgames[i][7]:
                    outcome = 2
                else:
                    outcome = 3

            c.execute("""INSERT INTO
                                    TEAMGAMES (
                                       SEASONID,SERIE,GAMEID,GAMEDATE,TEAM,HOMEAWAY,OPPONENT,OUTCOME,SCORE1,SCORE2,SHOTS1,SHOTS2,SAVES1,SAVES2,PENALTY1,PENALTY2,SCORE11,SCORE12,SCORE13,SCORE14,SCORE21,SCORE22,SCORE23,SCORE24,SHOTS11,SHOTS12,SHOTS13,SHOTS14,SHOTS21,SHOTS22,SHOTS23,SHOTS24)
                                    VALUES
                                        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (statsgames[i][0], statsgames[i][1], statsgames[i][2], statsgames[i][3], statsgames[i][5], 'A',
                       statsgames[i][4], outcome, statsgames[i][7], statsgames[i][6], statsgames[i][9],
                       statsgames[i][8], statsgames[i][11], statsgames[i][10], statsgames[i][13], statsgames[i][12],
                       statsgames[i][18], statsgames[i][19], statsgames[i][20], statsgames[i][21],
                       statsgames[i][14], statsgames[i][15], statsgames[i][16], statsgames[i][17],
                       statsgames[i][26], statsgames[i][27], statsgames[i][28], statsgames[i][29],
                       statsgames[i][22], statsgames[i][23], statsgames[i][24], statsgames[i][25]

                       ))

        else:
            pass

    conn.commit()


def calculate_team_strength(team,gamedate):

    import sqlite3
    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()
    print([gamedate,team])
    c.execute("SELECT * from lineups where gamedate = ? and TEAM = ? ",[gamedate,team])
    lineup = c.fetchall()
    lineup = lineup[0]

    currentserie=lineup[3]
    seasonid=lineup[2]

    c.execute("SELECT * FROM TEAMGAMES WHERE TEAM = ? and GAMEDATE < ? and SEASONID = ? ORDER BY GAMEDATE DESC", [team, gamedate, str(seasonid)])
    last5games = np.array(c.fetchall())

    n_games = min(len(last5games), 5)
    points = 0
    score = 0

    if n_games > 0:

        for i in range(0, n_games):
            points += (4 - int(last5games[i][7])) / n_games
            score += int(last5games[i][8]) / n_games
            score -= int(last5games[i][9]) / n_games

    else:
        points = 1.5
        score = 0

    print("Average score last 5: " + str(points))
    print("Average goal diff last 5: " + str(score))

    c.execute(
        "SELECT SEASONID, SERIE, COUNT(OUTCOME), SUM(4-OUTCOME) as POINTS FROM TEAMGAMES WHERE TEAM = ? and GAMEDATE < ? GROUP BY SEASONID, SERIE ORDER BY SEASONID",
        [team, gamedate])
    seasons = np.array(c.fetchall())

    n_seasons = len(seasons)

    season_points = -1
    sum = 0

    if n_seasons > 0:

        season_points = 0

        for i in range(0, n_seasons):

            fakt = 1

            if currentserie in ['SHL', 'Slutspel', 'Kvalserie']:
                if seasons[i][1] == 'HA':
                    fakt = 0.65
                elif seasons[i][1] == 'Div1':
                    fakt = 0.5

            if currentserie in ['HA']:
                if seasons[i][1] in ['SHL', 'Slutspel', 'Kvalserie']:
                    fakt = 1.25
                elif seasons[i][1] == 'Div1':
                    fakt = 0.7

            season = int(seasons[i][0])
            years_ago = seasonid - season

            if years_ago == 0:
                years_ago = 1

            season_points += float(seasons[i][3]) * fakt / float(seasons[i][2]) / (years_ago)
            sum += 1 / (years_ago)

        season_points = season_points / sum
        print("Average point / game last seasons: " + str(season_points))

    c.execute("SELECT FORNAME, SURNAME, PERSONNR FROM lineups where gameid = ? and team = ?", [lineup[1], team])
    lineup_team = np.array(c.fetchall())


    if len(lineup_team) > 0:

        player_score_sum = 0
        n_players = 0

        for i in range(0, len(lineup_team)):
            if get_player_score(lineup_team[i][0], lineup_team[i][1], lineup_team[i][2], gamedate) != 0:
                player_score_sum += get_player_score(lineup_team[i][0], lineup_team[i][1], lineup_team[i][2], gamedate)
                n_players+=1


    else:
        player_score_final = -999

    player_score_final = (player_score_sum / n_players)

    final_team_score = points * 0.4 + season_points * 0.2 + player_score_final * 0.2

    return final_team_score


def get_player_score(forname, surname, personnr, gamedate):

    # For other seasons add roster data

    import sqlite3
    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()

    current_year = int(gamedate[0:4])


    #Calculate lineup score

    c.execute("SELECT SEASONID, SUM(SCORE)/COUNT(SCORE), COUNT(SCORE) AS MATCHES FROM lineups WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and GAMEDATE < ? GROUP BY SEASONID ORDER BY SEASONID DESC",[forname,surname,personnr,gamedate])
    scrs = c.fetchall()

    lineup_score = 0
    total_weight = 0

    if len(scrs) > 0:

        for i in range(0,len(scrs)):
            weight = scrs[i][2]/(current_year-scrs[i][0]+1)
            lineup_score += scrs[i][1]*weight
            total_weight += weight

        lineup_score = lineup_score/total_weight


    #Calculate rosters score

    c.execute("SELECT SEASONID, GAMES, PLUS, MINUS FROM ROSTERS WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ?",[forname,surname,personnr])
    scrs = c.fetchall()

    roster_score = 0
    total_weight = 0

    if len(scrs) > 0:

        for i in range(0, len(scrs)):

            if scrs[i][2] == " ":
                plus = 0
            else:
                if scrs[i][2] == None:
                    plus = 0
                else:
                    plus = int(scrs[i][2])

            if scrs[i][3] == " ":
                minus = 0
            else:
                if scrs[i][3] == None:
                    minus = 0
                else:
                    minus = int(scrs[i][3])
            if scrs[i][1] != None:
                weight = scrs[i][1] / (current_year - scrs[i][0] + 1)
                roster_score += (plus - minus + 6) / scrs[i][1] * weight * 50
                total_weight += weight


        roster_score = roster_score / total_weight

    total_score = lineup_score * 0.7 + roster_score * 0.3


    return total_score