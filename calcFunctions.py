import numpy as np
import datetime
import calendar
from functions import add_months



def create_game_rating(lineup,c,team):

    output = []

    #Get some additional information from stats

    c.execute("SELECT * FROM stats where gameid = ?",[lineup[0][1]])
    stats = c.fetchall()

    print(stats)
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

        goals = lineup[i][15]
        PPgoals = lineup[i][16]
        SHgoals = lineup[i][17]
        assist = lineup[i][18]
        plus = lineup[i][19]
        minus = lineup[i][20]
        penalty = lineup[i][21]
        inPP = lineup[i][22]
        inBP = lineup[i][23]
        shots = lineup[i][24]
        saves = lineup[i][25]

        if lineup[i][6] == lineup[i][8]:
            comp = lineup[i][7]
        else:
            comp = lineup[i][6]

        compstat = 3 #Team score of competition
        #Half should come from players, half from form
        #Select from gamesmatchtable


        c.execute("SELECT SEASONID, SERIE, SUM(CASE WHEN OUTCOME = 1 THEN 3 WHEN OUTCOME = 2 THEN 2 WHEN OUTCOME = 3 THEN 1 ELSE 0 END) POINTS, COUNT(TEAM) as MATCHES FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? AND GAMEDATE < ? AND GAMEDATE > ? GROUP BY SEASONID, SERIE", [opponent, stats[0][0], stats[0][3], olddate])
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
            score += shots*2
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

        score = score + (score1-score2)*(compstat)

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





