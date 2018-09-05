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

seasonID = 9006
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

for i in range(0,1):
    #http://stats.swehockey.se/Game/Events/347351/
    #http://stats.swehockey.se/Game/LineUps/347351

    # Download Action data from each game
    stats = get_stats(gameVector[i])
    lineups = get_lineups(gameVector[i], stats[2], stats[3])
    actions = get_actions(gameVector[i], stats[2], stats[3])
    get_refs(gameVector[i])

    print(lineups)

#Save data to tables

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
        pass

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
c.close