from functions import isnumber
from functions import find_str
from functions import get_isolated_number
from functions import get_isolated_percent
from functions import get_period_stats
from get_lineups import get_lineups
from get_stats import get_stats
from get_actions import get_actions
from get_refs import get_refs
import urllib.request as urllib
import numpy as np

seasonID = 8121
scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)

nGames = 0
gameVector = []
lineVector = []


response = urllib.urlopen(scheduleUrl)
page_source = str(response.read())

line = ""

import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

#c.execute("""CREATE TABLE roster (
#                ID integer,
#                TEAM TEXT,
#                NUMBER integer,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                POSITION TEXT)""")

#c.execute("""CREATE TABLE lineups (
#                ID integer,
#                GAMEID integer,
#                HOMETEAM TEXT,
#                AWAYTEAM TEXT,
#                TEAM TEXT,
#                GAMEDATE TEXT,
#                NUMBER integer,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                POSITION TEXT,
#                START_PLAYER integer)""")

#c.execute("""CREATE TABLE events (
#                ID integer,
#                GAMEID integer,
#                PERIOD integer,
#                TIME TEXT,
#                EVENT TEXT,
#                TEAM TEXT,
#                NUMBER TEXT,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                EXTRA1 TEXT,
#                EXTRA2 TEXT)""")

#c.execute("""CREATE TABLE stats (
#                GAMEID integer,
#                GAMEDATE TEXT,
#                HOMETEAM TEXT,
#                AWAYTEAM TEXT,
#                HOMESCORE integer,
#                AWAYSCORE integer,
#                HOMESHOTS integer,
#                AWAYSHOTS integer,
#                HOMESAVES integer,
#                AWAYSAVES integer,
#                HOMEPENALTY integer,
#                AWAYPENALTY integer,
#                HSHOTS1 integer,
#                HSHOTS2 integer,
#                HSHOTS3 integer,
#                HSHOTS4 integer,
#                ASHOTS1 integer,
#                ASHOTS2 integer,
#                ASHOTS3 integer,
#                ASHOTS4 integer,
#                HSAVES1 integer,
#                HSAVES2 integer,
#                HSAVES3 integer,
#                HSAVES4 integer,
#                ASAVES1 integer,
#                ASAVES2 integer,
#                ASAVES3 integer,
#                ASAVES4 integer,
#                HPENALTY1 integer,
#                HPENALTY2 integer,
#                HPENALTY3 integer,
#                HPENALTY4 integer,
#                APENALTY1 integer,
#                APENALTY2 integer,
#                APENALTY3 integer,
#                APENALTY4 integer)""")

#c.execute("""CREATE TABLE refs (
#                GAMEID integer,
#                HOMETEAM TEXT,
#                AWAYTEAM TEXT,
#                REF1 TEXT,
#                REF2 TEXT,
#                LINE1 TEXT,
#                LINE2 TEXT)""")

for i in range(1,len(page_source)-10):

    if page_source[i:i+8] == "/Events/":

        gameID = 0

        for j in range(1,10):
            if isnumber(page_source[i+8+j]) == False:
                if gameID == 0:
                    gameID = page_source[i+8:i+8+j]
                    nGames += 1
                    gameVector.append(gameID)


#Download Lineup data from each game


for j in range(0,len(gameVector)):

    # Download Action data from each game
    stats = get_stats(gameVector[j])
    lineups = get_lineups(gameVector[j], stats[2], stats[3])
    [refs, lines] = get_refs(gameVector[j])

#Create roster table

    for i in range(0,len(lineups)):
        c.execute("SELECT ID as ID FROM roster where TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ?", [lineups[i][1],lineups[i][2],lineups[i][3],lineups[i][4]])
        hits = c.fetchall()

        c.execute("SELECT ID as ID FROM roster")
        ids = c.fetchall()

        if len(ids) > 0:
            id = max(ids)[0]+1
        else:
            id = 1

        if len(hits) == 0:

            if lineups[5] == "Goalies":
                position = "G"
            else:
                position = "D/F"

            c.execute("""INSERT INTO
                roster (
                    ID,TEAM,NUMBER,FORNAME,SURNAME,POSITION)
                VALUES
                    (?,?,?,?,?,?)""",
                      (id,lineups[i][1],lineups[i][2],lineups[i][3],lineups[i][4],position))

        else:
            pass

    conn.commit()

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
                            ID,GAMEID,HOMETEAM,AWAYTEAM,TEAM,GAMEDATE,NUMBER,FORNAME,SURNAME,POSITION,START_PLAYER)
                        VALUES
                            (?,?,?,?,?,?,?,?,?,?,?)""",
                      (id, lineups[i][0], stats[2], stats[3], lineups[i][1], stats[1], lineups[i][2], lineups[i][3], lineups[i][4], lineups[i][5], lineups[i][6]))

        else:
            pass

    conn.commit()

    events = get_actions(gameVector[j], stats[2], stats[3], c)


#Create event table

    for i in range(0, len(events)):
        c.execute(
            "SELECT ID as ID FROM events where GAMEID = ? and TIME = ? and EVENT = ? and TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ?",
            [events[i][0], events[i][2], events[i][3], events[i][4], events[i][5], events[i][6], events[i][7]])
        hits = c.fetchall()
        c.execute("SELECT ID as ID FROM events")
        ids = c.fetchall()

        if len(ids) > 0:
            id = max(ids)[0] + 1
        else:
            id = 1

        if len(hits) == 0:

            c.execute("""INSERT INTO
                            events (
                                ID,GAMEID,PERIOD,TIME,EVENT,TEAM,NUMBER,FORNAME,SURNAME,EXTRA1,EXTRA2)
                            VALUES
                                (?,?,?,?,?,?,?,?,?,?,?)""",
                      (id, events[i][0], events[i][1], events[i][2], events[i][3], events[i][4], events[i][5], events[i][6],events[i][7],events[i][8],events[i][9]))

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
                            GAMEID,
                            GAMEDATE,
                            HOMETEAM,
                            AWAYTEAM,
                            HOMESCORE,
                            AWAYSCORE,
                            HOMESHOTS,
                            AWAYSHOTS,
                            HOMESAVES,
                            AWAYSAVES,
                            HOMEPENALTY,
                            AWAYPENALTY,
                            HSHOTS1,
                            HSHOTS2,
                            HSHOTS3,
                            HSHOTS4,
                            ASHOTS1,
                            ASHOTS2,
                            ASHOTS3,
                            ASHOTS4,
                            HSAVES1,
                            HSAVES2,
                            HSAVES3,
                            HSAVES4,
                            ASAVES1,
                            ASAVES2,
                            ASAVES3,
                            ASAVES4,
                            HPENALTY1,
                            HPENALTY2,
                            HPENALTY3,
                            HPENALTY4,
                            APENALTY1,
                            APENALTY2,
                            APENALTY3,
                            APENALTY4)
                        VALUES
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (stats[0],
                   stats[1],
                   stats[2],
                   stats[3],
                   stats[4],
                   stats[5],
                   stats[6],
                   stats[7],
                   stats[8],
                   stats[9],
                   stats[10],
                   stats[11],
                   stats[12],
                   stats[13],
                   stats[14],
                   stats[15],
                   stats[16],
                   stats[17],
                   stats[18],
                   stats[19],
                   stats[20],
                   stats[21],
                   stats[22],
                   stats[23],
                   stats[24],
                   stats[25],
                   stats[26],
                   stats[27],
                   stats[28],
                   stats[29],
                   stats[30],
                   stats[31],
                   stats[32],
                   stats[33],
                   stats[34],
                   stats[35]
                   ))

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
                                GAMEID,HOMETEAM,AWAYTEAM,REF1,REF2,LINE1,LINE2)
                            VALUES
                                (?,?,?,?,?,?,?)""",
                      (stats[0],stats[1],stats[2],refs[0],refs[1],lines[1],lines[2]))

        else:
            pass

    conn.commit()

    print("Game " + str(stats[0]) + " loaded")

c.close