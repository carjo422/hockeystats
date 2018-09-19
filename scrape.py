from functions import isnumber
from functions import find_str
from functions import get_isolated_number
from functions import get_isolated_percent
from functions import get_period_stats
from functions import get_td_content
from get_lineups import get_lineups
from get_stats import get_stats
from get_actions import get_actions
from get_refs import get_refs
import urllib.request as urllib
from official_roster import get_official_roster
import numpy as np
import datetime

seasonID = 9171
seasonYear = 2019
serie = "SHL"
scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)

nGames = 0
gameVector = []
venueVector = []
audVector = []

lineVector = []


response = urllib.urlopen(scheduleUrl)
page_source = str(response.read())

page_source = page_source.replace("\\xc3\\xa5", "å")
page_source = page_source.replace("\\xc3\\xa4", "ä")
page_source = page_source.replace("\\xc2\\xa0", " ")
page_source = page_source.replace("\\xc3\\xa9", "é")
page_source = page_source.replace("\\xc3\\xb6", "ö")
page_source = page_source.replace("\\xc3\\x84", "Ä")
page_source = page_source.replace("\\xc3\\x85", "Å")
page_source = page_source.replace("\\xc3\\x96", "Ö")
page_source = page_source.replace("\\r", " ")
page_source = page_source.replace("\\n", " ")

line = ""

import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()



for i in range(1,len(page_source)-10):

    if page_source[i:i+8] == "/Events/":

        gameID = 0

        for j in range(1,10):
            if isnumber(page_source[i+8+j]) == False:
                if gameID == 0:
                    gameID = page_source[i+8:i+8+j]
                    nGames += 1
                    gameVector.append(gameID)

        audience = ""

        tds = get_td_content(page_source[i:max(len(page_source)-10,i+200)])

        inserted = 0

        for j in range(0,10):
            if isnumber(tds[j]) and inserted == 0:
                inserted = 1
                audVector.append(int(tds[j]))
                venueVector.append(tds[j+1])

#Download Lineup data from each game


for j in range(0,6):#len(gameVector)):

    # Download Action data from each game
    stats = get_stats(gameVector[j])
    lineups = get_lineups(gameVector[j],audVector[j],venueVector[j], seasonYear, stats[2], stats[3])
    rosters = get_official_roster(seasonID,seasonYear,serie)
    [refs, lines] = get_refs(gameVector[j],audVector[j],venueVector[j],seasonYear)

#Create lineup table

    for i in range(0,len(lineups)):
        c.execute("SELECT ID as ID FROM lineups where GAMEID = ? and TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ?", [lineups[i][0], lineups[i][1], lineups[i][2], lineups[i][3], lineups[i][4]])
        hits = c.fetchall()
        c.execute("SELECT ID as ID FROM lineups")
        ids = c.fetchall()

        if len(ids) > 0:
            id = max(ids)[0] + 1
        else:
            id = 1

        if len(hits) == 0:

            c.execute("""INSERT INTO
                        lineups (
                            ID,GAMEID,SEASONID,AUDIENCE,VENUE,HOMETEAM,AWAYTEAM,TEAM,GAMEDATE,NUMBER,FORNAME,SURNAME,POSITION,START_PLAYER)
                        VALUES
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (id, lineups[i][0], lineups[i][9], lineups[i][7], lineups[i][8], stats[2], stats[3], lineups[i][1], stats[1], lineups[i][2], lineups[i][3], lineups[i][4], lineups[i][5], lineups[i][6]))

        else:
            pass



    conn.commit()



    # Create roster table

    for i in range(0, len(rosters)):
        c.execute(
            "SELECT PERSONNR FROM rosters where TEAM = ? and PERSONNR = ?",
            (rosters[i][1], rosters[i][6]))
        hits = c.fetchall()

        if len(hits) == 0:

            c.execute("""INSERT INTO
                                rosters (
                                    SEASONID,TEAM,SERIE,NUMBER,SURNAME,FORNAME,PERSONNR,POSITION,HANDLE,LENGHT,WEIGHT,LAST_UPDATE)
                                VALUES
                                    (?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (rosters[i][0], rosters[i][1], rosters[i][2], rosters[i][3], rosters[i][4], rosters[i][5],
                       rosters[i][6], rosters[i][7], rosters[i][8], rosters[i][9], rosters[i][10],
                       str(datetime.datetime.now())[0:10]))

        else:
            pass

    conn.commit()

    events = get_actions(gameVector[j],audVector[j],venueVector[j], seasonYear, stats[2], stats[3], c)

#Create event table

    for i in range(0, len(events)):
        c.execute(
            "SELECT ID FROM events where GAMEID = ? and TIME = ? and EVENT = ? and TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ?",
            [events[i][0], events[i][2], events[i][3], events[i][4], events[i][5], events[i][7], events[i][6]])
        hits = c.fetchall()
        c.execute("SELECT ID as ID FROM events")
        ids = c.fetchall()

        if len(ids) > 0:
            id = max(ids)[0] + 1
        else:
            id = 1

        if len(hits) == 0:

            c.execute("""SELECT PERSONNR FROM rosters WHERE SEASONID = ? and TEAM = ? and NUMBER = ? and FORNAME = ? AND SURNAME = ? """, (seasonYear, events[i][4], events[i][5], events[i][7], events[i][6]))
            personnr = c.fetchall()

            if personnr == []:
                pnr = ""
            else:
                pnr = personnr[0][0]


            c.execute("""INSERT INTO
                            events (
                                ID,GAMEID,SEASONID,AUDIENCE,VENUE,PERIOD,TIME,EVENT,TEAM,NUMBER,PERSONNR,FORNAME,SURNAME,EXTRA1,EXTRA2)
                            VALUES
                                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (id,events[i][0],events[i][12],events[i][10],events[i][11], events[i][1], events[i][2], events[i][3], events[i][4], events[i][5],pnr, events[i][7],events[i][6],events[i][8],events[i][9]))

        else:
            pass

    conn.commit()

#Create stats table

    c.execute(
        "SELECT GAMEID as GAMEID FROM stats where GAMEID = ?",
        [stats[0]])

    hits = c.fetchall()

    if len(hits) == 0:

        c.execute("""INSERT INTO
                        stats (
                            SEASONID,SERIE,GAMEID,GAMEDATE,HOMETEAM,AWAYTEAM,HOMESCORE,AWAYSCORE,HOMESHOTS,AWAYSHOTS,HOMESAVES,AWAYSAVES,HOMEPENALTY,AWAYPENALTY,HSCORE1,HSCORE2,HSCORE3,HSCORE4,ASCORE1,ASCORE2,ASCORE3,ASCORE4,
                            HSHOTS1,HSHOTS2,HSHOTS3,HSHOTS4,ASHOTS1,ASHOTS2,ASHOTS3,ASHOTS4,HSAVES1,HSAVES2,HSAVES3,HSAVES4,ASAVES1,ASAVES2,ASAVES3,ASAVES4,HPENALTY1,HPENALTY2,HPENALTY3,HPENALTY4,APENALTY1,APENALTY2,APENALTY3,
                            APENALTY4)
                        VALUES
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (seasonYear,serie,stats[0],stats[1],stats[2],stats[3],stats[4],stats[5],stats[6],stats[7],stats[8],stats[9],stats[10],stats[11],stats[12],stats[13],stats[14],stats[15],stats[16],stats[17],stats[18],stats[19],stats[20],
                   stats[21],stats[22],stats[23],stats[24],stats[25],stats[26],stats[27],stats[28],stats[29],stats[30],stats[31],stats[32],stats[33],stats[34],stats[35],stats[36],stats[37],stats[38],stats[39],stats[40],
                   stats[41],stats[42],stats[43]))

    else:
        pass

    conn.commit()

#Create ref table

    for i in range(0, len(events)):
        c.execute(
            "SELECT GAMEID as GAMEID FROM refs where GAMEID = ?",
            [stats[0]])
        hits = c.fetchall()

        if len(hits) == 0:

            c.execute("""INSERT INTO
                            refs (
                                GAMEID,SEASONID,HOMETEAM,AWAYTEAM,REF1,REF2,LINE1,LINE2)
                            VALUES
                                (?,?,?,?,?,?,?,?)""",
                      (stats[0],seasonYear,refs[0],refs[1],stats[2],stats[3],lines[0],lines[1]))

        else:
            pass

    conn.commit()


#Update lineups with stats
    c.execute("SELECT TEAM, NUMBER FROM lineups where GAMEID = ?",[gameVector[j]])
    lineups = c.fetchall()

    for i in range(0,len(lineups)):
        c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?", ['Goal',gameVector[j], lineups[i][0],lineups[i][1]])
        goals = c.fetchall()[0][0]

        if goals == None:
            goals = 0

        c.execute("SELECT SUM(CASE WHEN EVENT = ? and EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['Goal','PP', gameVector[j], lineups[i][0], lineups[i][1]])
        PP = c.fetchall()[0][0]

        if PP == None:
            PP = 0

        c.execute("SELECT SUM(CASE WHEN EVENT = ? and EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['Goal','SH', gameVector[j], lineups[i][0], lineups[i][1]])
        SH = c.fetchall()[0][0]

        if SH == None:
            SH = 0

        c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?", ['Assist', gameVector[j], lineups[i][0], lineups[i][1]])
        assist = c.fetchall()[0][0]

        if assist == None:
            assist = 0

        c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?", ['1', gameVector[j], lineups[i][0], lineups[i][1]])
        plus = c.fetchall()[0][0]

        if plus == None:
            plus = 0

        c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['-1', gameVector[j], lineups[i][0], lineups[i][1]])
        minus = c.fetchall()[0][0]

        if minus == None:
            minus = 0

        c.execute("SELECT SUM(CASE WHEN EVENT = ? then CAST(EXTRA2 as INT) else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['Penalty', gameVector[j], lineups[i][0], lineups[i][1]])
        penalty = c.fetchall()[0][0]

        if penalty == None:
            penalty = 0

        c.execute("SELECT SUM(CASE WHEN EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['PP', gameVector[j], lineups[i][0], lineups[i][1]])
        activePP = c.fetchall()[0][0]

        if activePP == None:
            activePP = 0
        elif activePP > 1:
            activePP = 1

        c.execute("SELECT SUM(CASE WHEN EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['SH', gameVector[j], lineups[i][0], lineups[i][1]])
        activeBP = c.fetchall()[0][0]

        if activeBP == None:
            activeBP = 0
        elif activeBP > 1:
            activeBP = 1

        #Addera kod för shots/saves

        c.execute("SELECT EXTRA1, EXTRA2 from events where EVENT = ? and GAMEID = ? and TEAM = ? and NUMBER = ?",['Keeper stat', gameVector[j], lineups[i][0], lineups[i][1]])
        golieStats = c.fetchall()

        if golieStats == []:
            shotsAt = 0
            saves = 0
        else:
            print(golieStats)
            shotsAt = golieStats[0][0]
            saves = golieStats[0][1]
            print(shotsAt)
            print(saves)

        c.execute("UPDATE lineups SET GOALS = ?, PPGOALS = ?, SHGOALS = ?, ASSISTS = ?, PLUS = ?, MINUS = ?, PENALTY = ?, INPOWERPLAY = ?, INBOXPLAY = ?, SHOTSAT = ?, SAVES = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",
                  [goals, PP, SH, assist, plus, minus, penalty, activePP, activeBP, shotsAt, saves, gameVector[j], lineups[i][0], lineups[i][1]])

        conn.commit()


    #Team games table

    #c.execute("CREATE TABLE TEAMGAMES (SEASONID, SERIE, GAMEID, GAMEDATE, TEAM, HOMEAWAY, OPPONENT, OUTCOME, SCORE1, SCORE2, SHOTS1, SHOTS2, SAVES1, SAVES2, PENALTY1, PENALTY2, SCORE11, SCORE12, SCORE13, SCORE14, SCORE21, SCORE22, SCORE23, SCORE24, SHOTS11, SHOTS12, SHOTS13, SHOTS14, SHOTS21, SHOTS22, SHOTS23, SHOTS24)")

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

    #Standings table


    #Calculate the standings


#    c.execute("""CREATE TABLE standings as
#                SELECT
#                    ? as SEASONID,
#                    ? as SERIE
#                    ? as DATE
#                    distinct a.TEAM,


#(
#                SEASONID INTEGER,
#                SERIE INTEGER,
#                DATE TEXT,
#                TEAM TEXT,
#                WINS INTEGER,
#                OT_WINS INTEGER,
#                OT_LOSSES INTEGER,
#                LOSSES INTEGER,
#                SCORED INTEGER,
#                CONCEDED INTEGER,
#                DIFF INTEGER,
#                POINTS INTEGER,
#                POSITION INTEGER
#                )""")  #Pre match table

    print("Game " + str(stats[0]) + " loaded")






c.close



