import pandas as pd
import numpy as np
import openpyxl
from pandas import ExcelWriter
from functions import linreg

import sqlite3
conn = sqlite3.connect('/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/hockeystats.db')
c = conn.cursor()

def get_player_position(forname, surname, gamedate, team, seasonYear):
    c.execute("SELECT GAMEID, POSITION FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND GAMEDATE < ?",[forname, surname, gamedate])
    player = c.fetchall()

    position = "LD"
    handle = "L"

    if len(player) > 0:

        RW = 0
        LW = 0
        CE = 0
        LD = 0
        RD = 0
        GK = 0

        for i in range(0,len(player)):
            gameid = player[0][0]
            line = player[0][1]

            c.execute("SELECT b.POSITION FROM LINEUPS a LEFT JOIN ROSTERS b ON a.forname = b.forname AND a.surname = b.surname AND a.team = b.team WHERE GAMEID = ? AND a.TEAM = ? AND a.POSITION = ? AND b.SEASONID = ?",[gameid, team, line, seasonYear])
            pos = c.fetchall()

            nD = 0
            nO = 0

            nCE = 0
            nLW = 0
            nRW = 0
            nLD = 0
            nRD = 0
            nGK = 0

            nGolie = 0

            if len(pos) > 0:
                for j in range(0,len(pos)):
                    if pos[j][0] == 'CE':
                        nO += 1
                        nCE += 1
                    if pos[j][0] == 'RW':
                        nO += 1
                        nRW += 1
                    if pos[j][0] == 'LW':
                        nO += 1
                        nLW += 1
                    if pos[j][0] == 'LD':
                        nD += 1
                        nLD += 1
                    if pos[j][0] == 'RD':
                        nD += 1
                        nRD += 1
                    if pos[j][0] == 'GK':
                        nGK += 1

            if nO == 3:
                if nLD == 1:
                    RD+=1
                else:
                    LD+=1

            if nO < 3:
                if nGK > 0:
                    GK+=1
                elif nCE == 0:
                    CE+=1
                elif nRW == 0:
                    RW+=1
                else:
                    LW+=1

    if max(GK,LD,RD,LW,RW,CE) == GK:
        position = "GK"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == LD:
        position = "LD"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == RD:
        position = "RD"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == LW:
        position = "LW"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == RW:
        position = "RW"
        handle = "R"
    elif max(GK, LD, RD, LW, RW, CE) == CE:
        position = "CE"
        handle = "L"

    return position,handle

def get_player_data(team, gameid, gamedate, odds, seasonYear, serie, c, conn):

    #Get all players in current team

    c.execute("SELECT GAMEID FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 1 ",[seasonYear, team, gamedate])
    lst = c.fetchall()

    last_id = ''

    if len(lst) > 0:
        last_id = lst[0][0]

    c.execute("SELECT  FORNAME, SURNAME, PERSONNR, POSITION FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND gameid = ?",[team, seasonYear, last_id])
    players = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr','Line'])

    #If first game
    if len(players) == 0:
        c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND gamedate = ?",[team, seasonYear, gamedate])
        players = pd.DataFrame(c.fetchall(), columns=['Forname', 'Surname', 'Personnr','Line'])


    tot1 = 0
    tot2 = 0

    for i in range(0,len(players)):

        #############################################################################################################################
        #####                                              BASIC DATA + LINE                                                    #####
        #############################################################################################################################

        forname = players['Forname'][i]
        surname = players['Surname'][i]
        personnr = players['Personnr'][i]
        line = players['Line'][i]

        c.execute("SELECT POSITION, HANDLE, LENGHT, WEIGHT FROM ROSTERS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? ORDER BY SEASONID DESC",[forname, surname, personnr])
        rst = c.fetchall()

        position = ""
        handle = ""
        weight = ""
        length = ""

        if len(rst) > 0:
            position = rst[0][0]
            handle = rst[0][1]
            weight = rst[0][2]
            length = rst[0][3]

        c.execute("""SELECT GAMEDATE,
                            SEASONID,
                            SERIE,
                            GAMEDATE-PERSONNR,
                            GOALS,
                            ASSISTS,
                            PLUS,
                            MINUS,
                            CAST(INPOWERPLAY AS FLOAT),
                            CAST(INBOXPLAY AS FLOAT),
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END
                        FROM
                            LINEUPS
                        WHERE
                            (FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND TEAM = ? AND GAMEDATE < ?
                        OR
                            FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND TEAM = ? AND GAMEDATE < ?)
                        GROUP BY
                            FORNAME, SURNAME, PERSONNR, GAMEID
                        ORDER BY
                            GAMEDATE DESC""", ['1st Line', '2nd Line', '3rd Line', '4th Line', 'Extra players', forname, surname, personnr, team, gamedate, forname, surname, '', team, gamedate])

        sts = c.fetchall()

        #print(sts)

        #CURRENT SEASON LINE SCORE

        n_games_old = 0
        oldLine = [0,0,0,0,0]
        plus_minus = 0

        if len(sts) > 0:
            for j in range(0, len(sts)):
                if sts[j][1] <= seasonYear:
                    n_games_old += 1/(seasonYear*5-sts[j][1]*5+1)

                    oldLine[0] += sts[j][10]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[1] += sts[j][11]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[2] += sts[j][12]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[3] += sts[j][13]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[4] += sts[j][14]/(seasonYear*5-sts[j][1]*5+1)

                    plus_minus += (sts[j][6]*1.25+sts[j][7]*0.5)/(seasonYear*5-sts[j][1]*5+1) * 0.2


        # NUMBER OF GAMES LINE SCORE

        line_score_old = 0

        if n_games_old > 0:
            for j in range(0,len(oldLine)):
                oldLine[j] /= n_games_old

            plus_minus /= n_games_old

        line_score_old += oldLine[0] * 0.335
        line_score_old += oldLine[1] * 0.300
        line_score_old += oldLine[2] * 0.230
        line_score_old += oldLine[3] * 0.130
        line_score_old += oldLine[4] * 0.005

        if personnr != '':
            age = int(gamedate[0:4])-int(personnr[0:4])
        else:
            if n_games_old > 0:
                age = 18
            else:
                age = 30

        #FIND POSITION IF NOT AVAILABLE IN ROSTER

        if position == '':
            if line_score_old > 0.02 and plus_minus > 0.02:

                position, handle = get_player_position(forname, surname, gamedate, team, seasonYear)

        # ADJUST GK - THEY DONT SCORE

        if position == "GK":
            line_score_old = 0
            plus_minus = 0

        tot1 += line_score_old
        tot2 += plus_minus

        #ADJUST PLAYERS WITHOUT GAME HISTORY

        if n_games_old == 0:
            if age <= 18:
                line_score_old = 0.025
                plus_minus = 0.025
            elif age <= 21:
                line_score_old = 0.06
                plus_minus = 0.06
            elif age <= 24:
                line_score_old = 0.1
                plus_minus = 0.1
            else:
                line_score_old = 0.18
                plus_minus = 0.18

        #NO ADJUSTMENT ON AGE AT THIS STAGE


        #############################################################################################################################
        #####                                               HISTORIC SCORING                                                    #####
        #############################################################################################################################

        if personnr == '':
            c.execute("SELECT SEASONID, SERIE, COUNT(GAMEID), SUM(GOALS), SUM(ASSISTS), SUM(PLUS) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND TEAM = ? GROUP BY SEASONID ORDER by SEASONID",[forname, surname, team])
            hist = c.fetchall()
        else:
            c.execute("SELECT SEASONID, SERIE, COUNT(GAMEID), SUM(GOALS), SUM(ASSISTS), SUM(PLUS) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? GROUP BY SEASONID ORDER by SEASONID",[forname, surname, personnr])
            hist = c.fetchall()

        if len(hist) > 0:

            score_trend = pd.DataFrame(columns=['Year','nGames','goalsTeam','goalsPlayer','assistPlayer','plusPlayer','goalPercent','Weight'])

            for j in range(0,len(hist)):

                if personnr == '':
                    c.execute("SELECT COUNT(a.gameid), SUM(b.SCORE1) FROM LINEUPS a LEFT JOIN TEAMGAMES b ON a.gameid = b.gameid WHERE b.TEAM = a.TEAM AND a.SEASONID = ? AND forname = ? AND surname = ? AND a.team = ?",[hist[j][0], forname, surname, team])
                    goals = c.fetchall()
                else:
                    c.execute("SELECT COUNT(a.gameid), SUM(b.SCORE1) FROM LINEUPS a LEFT JOIN TEAMGAMES b ON a.gameid = b.gameid WHERE b.TEAM = a.TEAM AND a.SEASONID = ? AND forname = ? AND surname = ? AND personnr = ?",[hist[j][0], forname, surname, personnr])
                    goals = c.fetchall()

                if len(goals) > 0:
                    total_goals = goals[0][1]
                else:
                    total_goals = 0

                goalPercent = hist[j][3]/total_goals

                score_trend = score_trend.append({
                     'Year': seasonYear-hist[j][0],
                     'nGames': hist[j][2],
                     'goalsTeam': total_goals,
                     'goalsPlayer': hist[j][3],
                     'assistPlayer': hist[j][4],
                     'plusPlayer': hist[j][5],
                     'goalPercent': goalPercent,
                     'Weight': hist[j][2]/(seasonYear-hist[j][0]+1)
                }, ignore_index=True)


            #Calculate average scoring of player

            average_score_percent = 0
            average_assist_percent = 0
            average_plus_percent = 0
            total_weight = 0

            score_trend['s_weight'] = score_trend['goalPercent'] * score_trend['Weight']
            average_score_percent += score_trend['s_weight'].sum() / score_trend['Weight'].sum()

            score_trend['a_weight'] = score_trend['assistPlayer'] / score_trend['goalsTeam'] * score_trend['Weight']
            average_assist_percent += score_trend['a_weight'].sum() / score_trend['Weight'].sum()

            score_trend['p_weight'] = score_trend['plusPlayer'] / score_trend['goalsTeam'] * score_trend['Weight']
            average_plus_percent += score_trend['p_weight'].sum() / score_trend['Weight'].sum()

            total_weight = score_trend['Weight'].sum()

            #Calculate trend of scoring
            a=0
            b=0

            if len(hist) > 3:

                x = score_trend['goalPercent'].tolist()

                if hist[j][2] < 7:
                    x = (x[0:len(x)-1])

                a, b = linreg(range(len(x)), x)
            else:
                valid_trend = 0

            valid_trend = 1

            for t in range(0,len(hist)):
                if score_trend['Weight'][t] < 2:
                    valid_trend = 0

            if valid_trend == 1:
                trend = a

            st = str(score_trend.to_string())

            #print(forname, surname, position, handle, personnr, round(n_games_old, 1), round(line_score_old / 2 + plus_minus / 2, 3), line, age)

            #return forname, surname, position, handle, personnr, line, age, total_weight, round(line_score_old / 2 + plus_minus / 2, 3), average_score_percent, average_assist_percent, average_plus_percent, trend


get_player_data('Linköping HC', 393304, '2018-11-20', 0.65, 2019, 'SHL', c, conn)