from functions import isnumber
from functions import find_str
from functions import get_isolated_number
from functions import get_isolated_percent
from functions import get_period_stats
from functions import get_td_content
from functions import transform_date
from get_lineups import get_lineups
from get_stats import get_stats
from get_actions import get_actions
from get_refs import get_refs
import urllib.request as urllib
from calcFunctions import create_game_rating
from official_roster import get_official_roster
from get_year_statistics import get_year_statistics
from calcFunctions import create_teamgames
import numpy as np
import datetime

t=0
t_count = 1
seasonID = 9171
seasonYear = 2019
serie = "SHL"
scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)

nGames = 0
gameVector = []
venueVector = []
audVector = []
dateVector = []

lineVector = []


response = urllib.urlopen(scheduleUrl)
page_source = str(response.read())

line = ""

import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

#Check if vectors exist
c.execute("SELECT * FROM schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
sc = c.fetchall()

if len(sc) == 0:

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

    for i in range(1,len(page_source)-10):

        if isnumber(page_source[i:i+4]) and page_source[i+4] == '-' and isnumber(page_source[i+5:i+7]) and page_source[i+7] and isnumber(page_source[i+8:i+10]):
            dateVector.append(page_source[i:i+10])

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

    for j in range(0, len(gameVector)):
        c.execute("INSERT INTO schedule (SEASONID, SERIE, GAMEID, GAMEDATE, AUD, VENUE) VALUES (?,?,?,?,?,?)",[seasonYear,serie,gameVector[j],dateVector[j+1], audVector[j], venueVector[j]])


c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
gameVector = c.fetchall()
c.execute("SELECT GAMEDATE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
dateVector = c.fetchall()
c.execute("SELECT AUD from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
audVector = c.fetchall()
c.execute("SELECT VENUE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
venueVector = c.fetchall()

conn.commit()

#Get the seasons roster
rosters = get_official_roster(seasonID,seasonYear,serie)
# Create roster table

for i in range(0, len(rosters)):
    c.execute(
        "SELECT PERSONNR FROM rosters where SEASONID = ? and TEAM = ? and PERSONNR = ?",
        (seasonYear, rosters[i][1], rosters[i][6]))
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

#Add roster statistics
get_year_statistics(seasonID, seasonYear, serie)

for j in range(0,len(gameVector)):
    #Test if game exists

    c.execute("SELECT * FROM lineups where GAMEID = ?",[gameVector[j][0]])
    check = c.fetchall()

    if len(check) == 0:
        # Download Stats from each game
        stats = get_stats(gameVector[j][0], dateVector[j][0])
        # Download lineups data from game j
        lineups = get_lineups(gameVector[j][0],audVector[j][0],venueVector[j][0], seasonYear, stats[2], stats[3])
        #Download ref information from each game
        [refs, lines] = get_refs(gameVector[j][0],audVector[j][0],venueVector[j][0],seasonYear)

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
                                ID,GAMEID,SEASONID,SERIE,AUDIENCE,VENUE,HOMETEAM,AWAYTEAM,TEAM,GAMEDATE,NUMBER,FORNAME,SURNAME,POSITION,START_PLAYER,
                                GOALS, PPGOALS, SHGOALS, ASSISTS, PLUS, MINUS, PENALTY, INPOWERPLAY, INBOXPLAY, SHOTSAT, SAVES, SCORE, FINALSCORE, SCORE5, GOALS5, ASSIST5, GAMES5, SCORE_CURRENT, GOALS_CURRENT, ASSIST_CURRENT, GAMES_CURRENT)
                            VALUES
                                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)""",
                          (id, lineups[i][0], lineups[i][9], serie, lineups[i][7], lineups[i][8], stats[2], stats[3], lineups[i][1][0:10], stats[1], lineups[i][2], lineups[i][3], lineups[i][4], lineups[i][5], lineups[i][6]))

            else:
                pass



        conn.commit()

        # Get events data from each game
        events = get_actions(gameVector[j][0],audVector[j][0],venueVector[j][0], seasonYear, stats[2], stats[3], c)

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
                      (seasonYear,serie,stats[0],stats[1][0:10],stats[2],stats[3],stats[4],stats[5],stats[6],stats[7],stats[8],stats[9],stats[10],stats[11],stats[12],stats[13],stats[14],stats[15],stats[16],stats[17],stats[18],stats[19],stats[20],
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
        c.execute("SELECT TEAM, NUMBER, FORNAME, SURNAME, GAMEDATE FROM lineups where GAMEID = ?",[gameVector[j][0]])
        lineups = c.fetchall()

        for i in range(0,len(lineups)):
            c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?", ['Goal',gameVector[j][0], lineups[i][0],lineups[i][1]])
            goals = c.fetchall()[0][0]

            if goals == None:
                goals = 0

            c.execute("SELECT SUM(CASE WHEN EVENT = ? and EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['Goal','PP', gameVector[j][0], lineups[i][0], lineups[i][1]])
            PP = c.fetchall()[0][0]

            if PP == None:
                PP = 0

            c.execute("SELECT SUM(CASE WHEN EVENT = ? and EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['Goal','SH', gameVector[j][0], lineups[i][0], lineups[i][1]])
            SH = c.fetchall()[0][0]

            if SH == None:
                SH = 0

            c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?", ['Assist', gameVector[j][0], lineups[i][0], lineups[i][1]])
            assist = c.fetchall()[0][0]

            if assist == None:
                assist = 0

            c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?", ['1', gameVector[j][0], lineups[i][0], lineups[i][1]])
            plus = c.fetchall()[0][0]

            if plus == None:
                plus = 0

            c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['-1', gameVector[j][0], lineups[i][0], lineups[i][1]])
            minus = c.fetchall()[0][0]

            if minus == None:
                minus = 0

            c.execute("SELECT SUM(CASE WHEN EVENT = ? then CAST(EXTRA2 as INT) else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['Penalty', gameVector[j][0], lineups[i][0], lineups[i][1]])
            penalty = c.fetchall()[0][0]

            if penalty == None:
                penalty = 0

            c.execute("SELECT SUM(CASE WHEN EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['PP', gameVector[j][0], lineups[i][0], lineups[i][1]])
            activePP = c.fetchall()[0][0]

            if activePP == None:
                activePP = 0
            elif activePP > 1:
                activePP = 1

            c.execute("SELECT SUM(CASE WHEN EXTRA1 = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ?",['SH', gameVector[j][0], lineups[i][0], lineups[i][1]])
            activeBP = c.fetchall()[0][0]

            if activeBP == None:
                activeBP = 0
            elif activeBP > 1:
                activeBP = 1

            #Addera kod för shots/saves

            c.execute("SELECT EXTRA1, EXTRA2 from events where EVENT = ? and GAMEID = ? and TEAM = ? and NUMBER = ?",['Keeper stat', gameVector[j][0], lineups[i][0], lineups[i][1]])
            golieStats = c.fetchall()

            if golieStats == []:
                shotsAt = 0
                saves = 0
            else:
                shotsAt = golieStats[0][0]
                saves = golieStats[0][1]

            c.execute("SELECT * from lineups where GAMEID = ? and TEAM = ? and NUMBER = ?",[gameVector[j][0], lineups[i][0], lineups[i][1]])
            lineup = c.fetchall()


            if len(lineup) > 0:

                c.execute(
                    "UPDATE lineups SET GOALS = ?, PPGOALS = ?, SHGOALS = ?, ASSISTS = ?, PLUS = ?, MINUS = ?, PENALTY = ?, INPOWERPLAY = ?, INBOXPLAY = ?, SHOTSAT = ?, SAVES = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",
                    [goals, PP, SH, assist, plus, minus, penalty, activePP, activeBP, shotsAt, saves, gameVector[j][0], lineups[i][0], lineups[i][1]])

                conn.commit()

                c.execute("SELECT * from lineups where GAMEID = ? and TEAM = ? and NUMBER = ?",
                          [gameVector[j][0], lineups[i][0], lineups[i][1]])
                lineup = c.fetchall()

                score = create_game_rating(lineup, c, lineups[i][0])

                if len(score) < 4:
                    score = ['0','0','0','0']

                c.execute("UPDATE lineups SET SCORE = ?, FINALSCORE = ?, OFFSCORE = ?, DEFSCORE = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",[score[0], score[1], score[2], score[3], gameVector[j][0], lineups[i][0], lineups[i][1]])

                c.execute("SELECT PERSONNR from rosters where SEASONID = ? and TEAM = ? and NUMBER = ?",[seasonYear, lineups[i][0], lineups[i][1]])
                personnr = c.fetchall()

                persnr = ''

                if len(personnr) > 0:
                    persnr = personnr[0][0]

                c.execute("UPDATE lineups SET PERSONNR = ? WHERE SEASONID = ? and TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ?",[persnr, seasonYear, lineups[i][0], lineups[i][1], lineups[i][2], lineups[i][3]])

                conn.commit()

                # Update lineups with old stats

                # Last five games

                c.execute("SELECT SCORE, GOALS, ASSISTS, GAMEDATE, TEAM, FORNAME, SURNAME FROM lineups WHERE GAMEDATE < ? and GAMEDATE > ? and FORNAME = ? and SURNAME = ? and PERSONNR = ? ORDER BY GAMEDATE DESC",[lineups[i][4],transform_date(lineups[i][4],20), lineups[i][2], lineups[i][3], persnr])
                output = np.array(c.fetchall())

                games5 = min(len(output),5)

                score5 = 0
                goals5 = 0
                assist5 = 0

                for k in range(0,games5):
                    score5 += float(output[k][0]) / games5
                    goals5 += float(output[k][1]) / games5
                    assist5 += float(output[k][2]) / games5

                # Current season

                c.execute("SELECT SCORE, GOALS, ASSISTS, GAMEDATE, TEAM, FORNAME, SURNAME FROM lineups WHERE SEASONID = ? and FORNAME = ? and SURNAME = ? and PERSONNR = ? ORDER BY GAMEDATE DESC",[seasonYear, lineups[i][2],lineups[i][3], persnr])
                output = np.array(c.fetchall())

                gamescurr = len(output)

                scorecurr = 0
                goalscurr = 0
                assistcurr = 0

                for k in range(0, gamescurr):
                    scorecurr += float(output[k][0]) / gamescurr
                    goalscurr += float(output[k][1]) / gamescurr
                    assistcurr += float(output[k][2]) / gamescurr




                c.execute("""UPDATE lineups SET SCORE5 = ?, GOALS5 = ?, ASSIST5 = ?, SCORE_CURRENT = ?, GOALS_CURRENT = ?, ASSIST_CURRENT = ?, GAMES5 = ?, GAMES_CURRENT = ?
                           WHERE GAMEID = ? and PERSONNR = ? and FORNAME = ? and SURNAME = ?""",
                          [score5, goals5, assist5, scorecurr, goalscurr, assistcurr, games5, gamescurr, gameVector[j][0], persnr, lineups[i][2], lineups[i][3]])

            conn.commit()


        #Create teamgames table

        create_teamgames(seasonYear, serie)

        #Standings table

        c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(CASE WHEN OUTCOME = 1 then 1 else 0 end) as WINS, SUM(CASE WHEN OUTCOME = 2 then 1 else 0 end) as OT_WINS, SUM(CASE WHEN OUTCOME = 3 then 1 else 0 end) as OT_LOSS,
                     SUM(CASE WHEN OUTCOME = 4 then 1 else 0 end) as LOSS,  SUM(CASE WHEN OUTCOME = 1 then 3 WHEN OUTCOME = 2 then 2 WHEN OUTCOME = 1 then 1 else 0 end) as POINTS, SUM(SCORE1) as G, SUM(SCORE2) as C,
                     SUM(SCORE1)-SUM(SCORE2) as D FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM""",[str(seasonYear),serie])

        standings = c.fetchall()

        standings = np.array(standings)


        np.sort(standings, axis=0)

        #print(standings)




        print("Game " + str(stats[0]) + " loaded")
    else:
        print("Game already loaded")

    if t_count == 1:
        t+=1
        print(str(t) + "/" + str(len(gameVector)) + " done")


c.close



