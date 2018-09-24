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
            line = '0. MV'
        elif lineup[i][13] == '1st Line':
            line = '1. Line'
        elif lineup[i][13] == '2nd Line':
            line = '2. Line'
        elif lineup[i][13] == '3rd Line':
            line = '3. Line'
        elif lineup[i][13] == '4th Line':
            line = '4. Line'
        else:
            line = 'Extra'

    # Get player position

        c.execute("SELECT position from rosters where SEASONID = ? and TEAM = ? and SERIE = ? and NUMBER = ?",[lineup[i][2],team,lineup[i][3],lineup[i][10]])
        position = c.fetchall()

        if len(position) > 0:
            position = position[0][0]
        else:
            position = ""

    # Get lineup information

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

        c.execute("SELECT * FROM TEAMGAMES WHERE TEAM = ? and GAMEDATE < ? and SEASONID = ? ORDER BY GAMEDATE DESC",[comp, gamedate, str(lineup[i][2])])
        last5games = np.array(c.fetchall())

        n_games = min(len(last5games),5)
        points = 0
        score = 0

        if n_games > 0:

            for i in range(0,n_games):
                points+= (4-int(last5games[i][7])) / n_games
                score+= int(last5games[i][8]) / n_games
                score-= int(last5games[i][9]) / n_games

        else:
            points= -1
            score = -1

        c.execute("SELECT SEASONID, SERIE, COUNT(OUTCOME), SUM(4-OUTCOME) as POINTS FROM TEAMGAMES WHERE TEAM = ? and GAMEDATE < ? GROUP BY SEASONID, SERIE ORDER BY SEASONID",[comp, gamedate])
        seasons = np.array(c.fetchall())

        n_seasons = len(seasons)

        season_points = -1
        sum = 0

        if n_seasons > 0:

            season_points = 0

            for i in range(0,n_seasons):
                season = int(seasons[i][0])
                years_ago = seasonid-season

                season_points += float(seasons[i][3]) / float(seasons[i][2]) / (years_ago+1)
                sum += 1 / (years_ago+1)


            season_points = season_points/sum

        c.execute("SELECT FORNAME, SURNAME, PERSONNR FROM lineups where gameid = ? and team = ?",[gameid, comp])
        opposition_team = np.array(c.fetchall())

        if len(opposition_team) > 0:

            player_score_sum = 0
            n_players = 0

        #CHANGE THIS TO ROSTER

            for i in range(0,len(opposition_team)):
                c.execute("SELECT SEASONID, SERIE, SUM(SCORE)/COUNT(SCORE) as SCORE FROM lineups WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and GAMEDATE < ?",[opposition_team[i][0],opposition_team[i][1],opposition_team[i][2],gamedate])
                player_scores = c.fetchall()

                if len(player_scores) > 0 and player_scores[0][0]:
                    player_score_final = mean_list(player_scores,2)
                else:
                    player_score_final = -999

        else:
            player_score_final = -999

        #print(player_score_final)

        compstat = 3

        olddate = stats[0][3]
        c.execute("SELECT SEASONID, SERIE, SUM(CASE WHEN OUTCOME = 1 THEN 3 WHEN OUTCOME = 2 THEN 2 WHEN OUTCOME = 3 THEN 1 ELSE 0 END) POINTS, COUNT(TEAM) as MATCHES FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? AND GAMEDATE < ? AND GAMEDATE >= ? GROUP BY SEASONID, SERIE", [opponent, stats[0][0], stats[0][3], olddate])
        form = c.fetchall()


        if "D" in position:

            score = 0

            score += goals * 12
            score += PPgoals * 6
            score += SHgoals * 12
            score += assist * 6
            score += plus * 5
            score += minus * -8
            score += inPP * 5
            score += inBP * 5
            score -= penalty * 4

            #shots against code
            #boast for conceding few goals
            #Goalie save % contribution

        elif position == "GK":

            score = 0

            score += assist * 10
            score += plus * 5
            score += minus *-5
            score += shots*2.6
            score += (shots-saves)*-20
            score -= penalty * 10


        else:

            score = 0

            score += goals * 12
            score += PPgoals * 6
            score += SHgoals * 12
            score += assist * 8
            score += plus * 6
            score += minus * -7
            score += inPP * 5
            score += inBP * 5
            score -= penalty * 6


            # shots against code
            # boast for conceding few goals

        score += (score1-score2)*(compstat)

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

    playerScore = [score, finalScore]

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





