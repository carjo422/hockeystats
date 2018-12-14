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
        score1 = stats[0][6]
        score2 = stats[0][7]
        shots1 = stats[0][8]
        shots2 = stats[0][9]
    else:
        opponent = stats[0][4]
        score1 = stats[0][7]
        score2 = stats[0][6]
        shots1 = stats[0][9]
        shots2 = stats[0][8]

    # Get date and id
    gamedate = lineup[0][9]
    seasonid = lineup[0][2]
    gameid = lineup[0][1]

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
    shots = lineup[0][25]
    saves = lineup[0][26]

    if lineup[0][6] == lineup[0][8]:
        comp = lineup[0][7]
    else:
        comp = lineup[0][6]

    # How good is the competition

    opp_score_simple = calculate_team_strength_simple(opponent,gamedate,c)

    #Check if score is already in team score table
    c.execute("Update TEAMGAMES SET OPP_SCORE_SIMPLE = ? WHERE GAMEID = ? AND TEAM = ?",[opp_score_simple, lineup[0][1], lineup[0][8]])
    conn.commit()

    #Calculate score for player

    score = 0
    offScore = 0
    defScore = 0

    if "D" in position:

        score += goals * 12 + PPgoals * 6 + SHgoals * 12 + assist * 8 + plus * 8 + minus * -8 - penalty * 2 + 8
        #offScore += goals * 12 + PPgoals * 6 + SHgoals * 12 + assist * 8 + plus * 8

        #score += (shots * 2.6 + (shots - saves) * -20) / 4
        #defScore += (shots * 2.6 + (shots - saves) * -20) / 4 + minus * -8 + 5

    elif position == "GK":

        score += shots * 2.6 + (shots - saves) * -20

    else:

        score += goals * 12 + PPgoals * 6 + SHgoals * 12 + assist * 8 + plus * 8 + minus * -8 - penalty * 4 + 5
        #offScore += goals * 12 + PPgoals * 6 + SHgoals * 12 + assist * 8 + plus * 8

        #score += (shots * 2.6 + (shots - saves) * -20) / 10
        #defScore += (shots * 2.6 + (shots - saves) * -20) / 10 + minus * -8 + 5


    if score < -10:
        finalScore = 1
    elif score >= -10 and score < 10:
        finalScore = 2
    elif score >= 10 and score < 27:
        finalScore = 3
    elif score >= 27 and score < 52:
        finalScore = 4
    elif score >= 52:
        finalScore = 5

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


def calculate_team_strength(team,gamedate,lineup_in,c):

    ######################################################## CODE TO GET AVERAGE SCORE FROM LAST GAMES ##############################################################


    c.execute("SELECT * from lineups where gamedate < ? and TEAM = ? order by gamedate DESC",[gamedate,team])
    lineup = c.fetchall()

    if len(lineup) > 0:

        lineup = lineup[0]

        currentserie=lineup[3]
        seasonid=lineup[2]
        gameid = lineup[1]

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

        c.execute("SELECT SEASONID, SERIE, COUNT(OUTCOME), SUM(4-OUTCOME) as POINTS FROM TEAMGAMES WHERE TEAM = ? and GAMEDATE < ? GROUP BY SEASONID, SERIE ORDER BY SEASONID",[team, gamedate])
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

        # If lineup is sent into the function, use that one otherwise get data from the lineup table
        if lineup_in == "":
            c.execute("SELECT FORNAME, SURNAME, PERSONNR, POSITION FROM lineups where gameid = ? and team = ?", [lineup[1], team])
            lineup_team = np.array(c.fetchall())
        else:
            lineup_team = lineup_in

        #If there is a lineup
        if len(lineup_team) > 0:

            player_score_sum = 0
            n_players = 0

            for i in range(0, len(lineup_team)):

                #If lineup is not sent into the function
                if lineup_in == "":

                    forname = lineup_team[i][0]
                    surname = lineup_team[i][1]
                    personnr = lineup_team[i][2]
                    position = lineup_team[i][3]

                #If it is
                else:

                    forname = ""
                    surname = ""
                    personnr = ""
                    position = ""

                    if lineup_team[i][1] == team:

                        forname = lineup_team[i][3]
                        surname = lineup_team[i][4]

                        c.execute("SELECT personnr FROM ROSTERS WHERE TEAM = ? AND SEASONID = ? AND FORNAME = ? AND SURNAME = ?",[team,seasonid,forname,surname]) #Get personnr from rosters
                        pr = c.fetchall()

                        if len(pr) > 0:
                            personnr = pr[0][0]
                        else:
                            personnr = ""

                        position = lineup_team[i][5]

                p_score = get_player_score(forname, surname, personnr, gamedate, gameid, c)

                if position in ["Goalies","3rd Line","4th Line"]:
                    player_score_sum += p_score/2
                elif position in ["1st Line", "2nd Line"]:
                    player_score_sum += p_score

                else:
                    p_score = 0

                if p_score != 0:
                    n_players+=1


        else:
            player_score_final = -999

        player_score_final = 0

        if n_players > 0:
            player_score_final = (player_score_sum / n_players)

        final_team_score = points * 0 + season_points * 0 + player_score_final * 0.5

    else:
        final_team_score = 2
        points = 0
        season_points = 0
        player_score_final = 2

    return [final_team_score, points, season_points, player_score_final]


def get_player_score(forname, surname, personnr, gamedate, gameid, c):

    current_year = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        current_year+=1

    #Calculate lineup score

    c.execute("SELECT SEASONID, SUM(SCORE)/COUNT(SCORE), COUNT(SCORE) AS MATCHES, SERIE FROM lineups WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and GAMEDATE < ? AND SEASONID = ? GROUP BY SEASONID, SERIE ORDER BY SEASONID DESC",[forname,surname,personnr,gamedate,current_year])
    scrs = c.fetchall()

    if len(scrs) > 0:
        lineup_score = scrs[0][1]*scrs[0][2]*0.3
        lineup_weight = scrs[0][2]*0.3
    else:
        lineup_score = 0
        lineup_weight = 0

    #Calculate rosters score

    c.execute("SELECT SEASONID, GAMES, ROSTER_SCORE_FINAL FROM ROSTERS WHERE FORNAME = ? and SURNAME = ? and PERSONNR = ? and SEASONID < ?",[forname,surname,personnr,current_year])
    scrs = c.fetchall()

    roster_score = 0
    roster_score_final = 0
    roster_weight = 0

    if len(scrs) > 0:
        for i in range(0,len(scrs)):
            if scrs[i][2] != "" and scrs[i][2] != None:
                roster_score = scrs[i][2]
            else:
                roster_score = 0

            if scrs[i][1] != None:
                weight = scrs[i][1] / (current_year-scrs[i][0])
            else:
                weight = 0

            roster_score_final += roster_score * weight
            roster_weight += weight


    if roster_weight + lineup_weight > 0:

        total_score = (lineup_score + roster_score_final)/(roster_weight + lineup_weight)

    else:
        total_score = 5

    if (roster_weight + lineup_weight) < 20:

        total_score *= ((roster_weight + lineup_weight)/20)**(1/2)



    return total_score



def calculate_team_strength_simple(team,gamedate,c):

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




    return points*4/3+1