import numpy as np
import datetime
import calendar

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

        c.execute("SELECT position from rosters where SEASONID = ? and TEAM = ? and SERIE = ? and NUMBER = ?",[lineup[i][2],team,lineup[i][3],lineup[i][10]])
        position = c.fetchall()

        if len(position) > 0:
            position = position[0][0]
        else:
            position = ""

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

        #Select from rosters

        if "D" in position:

            score = 0

            score += goals*10
            score += PPgoals*5
            score += SHgoals*10
            score += assist*5
            score += plus*5
            score += minus*-8
            score += inPP * 5
            score += inBP * 5
            score += ((18+compstat*3)-shots2)*1.5 #shots against

        elif position == "GK":

            score = 0

            score += assist * 10
            score += plus * 5
            score += minus *-5
            score += shots*2.6
            score += (shots-saves)*-20

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

            score += (shots1 - (18 + (5.5-compstat) * 3)) * 1.5  # Competition

        score += (score1-score2)*(compstat)

        if homeaway == 2:
            score += 4

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





