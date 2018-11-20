import pandas as pd
import numpy as np
import openpyxl
from pandas import ExcelWriter

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
                    if pos[i][0] == 'CE':
                        nO += 1
                        nCE += 1
                    if pos[i][0] == 'RW':
                        nO += 1
                        nRW += 1
                    if pos[i][0] == 'LW':
                        nO += 1
                        nLW += 1
                    if pos[i][0] == 'LD':
                        nD += 1
                        nLD += 1
                    if pos[i][0] == 'RD':
                        nD += 1
                        nRD += 1
                    if pos[i][0] == 'GK':
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

    c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND gameid = ?",[team, seasonYear, last_id])
    players = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr'])

    #If first game
    if len(players) == 0:
        c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND gamedate = ?",[team, seasonYear, gamedate])
        players = pd.DataFrame(c.fetchall(), columns=['Forname', 'Surname', 'Personnr'])


    tot1 = 0
    tot2 = 0

    for i in range(0,len(players)):

        forname = players['Forname'][i]
        surname = players['Surname'][i]
        personnr = players['Personnr'][i]

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

        if position == '':
            if line_score_old > 0.02 and plus_minus > 0.02:

                position, handle = get_player_position(forname, surname, gamedate, team, seasonYear)

        if position == "GK":
            line_score_old = 0
            plus_minus = 0

        tot1 += line_score_old
        tot2 += plus_minus

        print(forname, surname, position, handle, personnr, round(n_games_old,1), round(line_score_old,3), round(plus_minus,2), age)

        #CURRENT SEASON SCORE TREND
        #LAST SEASON SCORE TREND
        #SECOND LAST SEASON SCORE TREND
        #THIRD LAST SEASON SCORE TREND

    print("TOT", tot1, tot2)

get_player_data('Linköping HC', 393304, '2018-09-15', 0.65, 2019, 'SHL', c, conn)