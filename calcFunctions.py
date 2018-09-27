import numpy as np
import datetime
import calendar
import sqlite3

from functions import mean_list

import sqlite3


def create_game_rating(lineup,team,c,conn):

    output = []

    #Get some information from stats
    c.execute("SELECT * FROM stats where gameid = ?",[lineup[0][1]])
    stats = c.fetchall()


    #Transform data from stats

    #Get home/away score
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



    # Get date and id
    gamedate = lineup[0][9]
    seasonid = lineup[0][2]
    gameid = lineup[0][1]

    # Get player line

    if lineup[0][13] == 'Goalies':
        line = 0
    elif lineup[0][13] == '1st Line':
        line = 1
    elif lineup[0][13] == '2nd Line':
        line = 2
    elif lineup[0][13] == '3rd Line':
        line = 3
    elif lineup[0][13] == '4th Line':
        line = 4
    else:
        line = 5

    # Get player position

    c.execute("SELECT position from rosters where SEASONID = ? and TEAM = ? and SERIE = ? and NUMBER = ?",[lineup[0][2],team,lineup[0][3],lineup[0][10]])
    position = c.fetchall()

    if len(position) > 0:
        position = position[0][0]
    else:
        position = ""

    # Get lineup information

    currentserie = lineup[0][3]
    goals = lineup[0][16]
    PPgoals = lineup[0][17]
    SHgoals = lineup[0][18]
    assist = lineup[0][19]
    plus = lineup[0][20]
    minus = lineup[0][21]
    penalty = lineup[0][22]
    inPP = lineup[0][23]
    inBP = lineup[0][24]
    shots = lineup[0][25]
    saves = lineup[0][26]

    if lineup[0][6] == lineup[0][8]:
        comp = lineup[0][7]
    else:
        comp = lineup[0][6]

    # How good is the competition

    #Check if score is already in team score table
    c.execute("SELECT SCORE FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?", [gameid, comp])
    cstat = c.fetchall()

    if len(cstat) > 0:
        compstat = cstat[0][0]
    else:

        [compstat, form_score, last_seasons_score, player_score] = calculate_team_strength(comp,gamedate,c)
        c.execute("INSERT INTO TEAMSCORE (SEASONID, SERIE, GAMEID, GAMEDATE, TEAM, SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE) VALUES (?,?,?,?,?,?,?,?,?)",[stats[0][0], stats[0][1], gameid, gamedate, comp, compstat, form_score, last_seasons_score, player_score])
        conn.commit()
        print(compstat)


    #Calculate score for player

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


    #score += (compstat-1)*5


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



def create_teamgames(seasonYear, serie,c):
#Team games table

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

            c.execute("""INSERT INTO TEAMGAMES (SEASONID,SERIE,GAMEID,GAMEDATE,TEAM,HOMEAWAY,OPPONENT,OUTCOME,SCORE1,SCORE2,SHOTS1,SHOTS2,SAVES1,SAVES2,PENALTY1,PENALTY2,SCORE11,SCORE12,SCORE13,SCORE14,SCORE21,SCORE22,SCORE23,SCORE24,SHOTS11,SHOTS12,SHOTS13,SHOTS14,SHOTS21,SHOTS22,SHOTS23,SHOTS24)
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


def calculate_team_strength(team,gamedate,c):

    ######################################################## CODE TO GET AVERAGE SCORE FROM LAST GAMES ##############################################################

    c.execute("SELECT * from lineups where gamedate = ? and TEAM = ? ",[gamedate,team])
    #print([gamedate,team])
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
            points += (4 - int(last5games[i][7])) / 5
            score += int(last5games[i][8]) / 5
            score -= int(last5games[i][9]) / 5

        points += (5-n_games)*0.3

    else:
        points = 1.5
        score = 0

    ####################################################### CODE TO GET AVERAGE SCORE FROM LAST SEASONS #############################################################

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

            season_points += float(seasons[i][3]) * fakt / (years_ago) * float(seasons[i][2])
            sum += 1 / (years_ago) * float(seasons[i][2]) * float(seasons[i][2])

        season_points = season_points / sum


    ####################################################### CODE TO GET SCORE BASED ON PLAYERS #############################################################


    c.execute("SELECT FORNAME, SURNAME, PERSONNR FROM lineups where gameid = ? and team = ?", [lineup[1], team])
    lineup_team = np.array(c.fetchall())

    if len(lineup_team) > 0:

        player_score_sum = 0
        n_players = 0

        for i in range(0, len(lineup_team)):
            p_score = get_player_score(lineup_team[i][0], lineup_team[i][1], lineup_team[i][2], gamedate,c)
            player_score_sum += p_score

            if p_score != 0:
                n_players+=1

            #print([lineup_team[i][0],lineup_team[i][1],p_score])


    else:
        player_score_final = -999

    player_score_final = (player_score_sum / n_players)

    #print(player_score_sum)

    final_team_score = points * 0.3 + season_points * 0.2 + player_score_final * 0.4

    return [final_team_score, points, season_points, player_score_final]


def get_player_score(forname, surname, personnr, gamedate,c):

    current_year = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        current_year+=1


    #Calculate lineup score

    c.execute("SELECT SEASONID, SUM(SCORE)/COUNT(SCORE), COUNT(SCORE) AS MATCHES FROM lineups WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and GAMEDATE < ? GROUP BY SEASONID ORDER BY SEASONID DESC",[forname,surname,personnr,gamedate])
    scrs = c.fetchall()

    #print(scrs)

    #c.execute("SELECT SEASONID, SCORE, GOALS, ASSISTS FROM lineups WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and GAMEDATE < ? ORDER BY SEASONID DESC",[forname, surname, personnr, gamedate])
    #test = c.fetchall()

    #print(test)

    lineup_score = 0
    total_weight = 0

    if len(scrs) > 0:

        for i in range(0,len(scrs)):
            weight = scrs[i][2]/(current_year-scrs[i][0]+1)
            lineup_score += scrs[i][1]*weight
            total_weight += weight

        lineup_score = lineup_score/total_weight


    #Calculate rosters score

    c.execute("SELECT SEASONID, GAMES, PLUS, MINUS FROM ROSTERS WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and SEASONID < ?",[forname,surname,personnr,current_year])
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

        if total_weight > 0:
            roster_score = roster_score / total_weight
        else:
            roster_score = 0

    total_score = lineup_score * 0.7 + roster_score * 0.3

    return total_score