import datetime
import urllib.request as urllib

import numpy as np

from calcFunctions import create_game_rating
from calcFunctions import create_teamgames
from functions import get_td_content
from functions import isnumber
from functions import transform_date
from scfiles.get_actions import get_actions
from scfiles.get_lineups import get_lineups
from scfiles.get_refs import get_refs
from scfiles.get_stats import get_stats
from scfiles.get_year_statistics import get_year_statistics
from scfiles.official_roster import get_official_roster
from calcFunctions import calculate_team_strength
from create_pre_match_analysis import create_pre_match_analysis


#To get feedback on how many games to update
t=0
t_count = 0 # Counts number of update

#Input variables on seasons
#seasonID = 7157
#seasonYear = 2017
#serie = "HA"
#score_update = "New" #New if only fill with new scores

def scrape_sh(seasonID, seasonYear, serie, score_update):
    #Vectors to scrape in first step
    gameVector = []
    venueVector = []
    audVector = []
    dateVector = []
    lineVector = []

    #Read in season schedule
    scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)
    response = urllib.urlopen(scheduleUrl)
    page_source = str(response.read())

    #Establish connection to database
    import sqlite3
    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()

    #Check if vectors exist
    c.execute("SELECT * FROM schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    sc = c.fetchall()

    if len(sc) > 0:
        c.execute("DELETE FROM SCHEDULE")

    #If vectors dont exist then get vectors


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

        if isnumber(page_source[i:i + 4]) and page_source[i + 4] == '-' and isnumber(page_source[i + 5:i + 7]) and page_source[i + 7] and isnumber(page_source[i + 8:i + 10]):
            currdate = page_source[i:i + 10]

        if page_source[i:i+8] == "/Events/":

            gameID = 0

            for j in range(1,10):



                if isnumber(page_source[i+8+j]) == False:
                    if gameID == 0:
                        gameID = page_source[i+8:i+8+j]
                        gameVector.append(gameID)
                        dateVector.append(currdate)

            audience = ""

            tds = get_td_content(page_source[i:max(len(page_source)-10,i+200)])

            inserted = 0

            for j in range(0,10):
                if isnumber(tds[j]) and inserted == 0:
                    inserted = 1
                    audVector.append(int(tds[j]))
                    venueVector.append(tds[j+1])

    for j in range(0, len(gameVector)):
        c.execute("INSERT INTO schedule (SEASONID, SERIE, GAMEID, GAMEDATE, AUD, VENUE) VALUES (?,?,?,?,?,?)",[seasonYear,serie,gameVector[j],dateVector[j], audVector[j], venueVector[j]])


    c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    gameVector = c.fetchall()
    c.execute("SELECT GAMEDATE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    dateVector = c.fetchall()
    c.execute("SELECT AUD from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    audVector = c.fetchall()
    c.execute("SELECT VENUE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    venueVector = c.fetchall()

    conn.commit()

    ########################################################################################################################
    ################################    Get game specific statistics (Lineups)    ##########################################
    ########################################################################################################################

    #Loop through games
    for j in range(0,len(gameVector)):

        #Check if game already has been updated, then skip update

        c.execute("SELECT * FROM lineups where GAMEID = ?",[gameVector[j][0]])
        check = c.fetchall()

        if len(check) == 0:

            stats = get_stats(gameVector[j][0], dateVector[j][0])
            lineups = get_lineups(gameVector[j][0],audVector[j][0],venueVector[j][0], seasonYear, stats[2], stats[3])
            [refs, lines] = get_refs(gameVector[j][0],audVector[j][0],venueVector[j][0],seasonYear)

            # Create stats table
            c.execute("SELECT GAMEID as GAMEID FROM stats where GAMEID = ?",[stats[0]])

            hits = c.fetchall()

            if len(hits) == 0:

                c.execute("""INSERT INTO
                                stats (
                                    SEASONID,SERIE,GAMEID,GAMEDATE,HOMETEAM,AWAYTEAM,HOMESCORE,AWAYSCORE,HOMESHOTS,AWAYSHOTS,HOMESAVES,AWAYSAVES,HOMEPENALTY,AWAYPENALTY,HSCORE1,HSCORE2,HSCORE3,HSCORE4,ASCORE1,ASCORE2,ASCORE3,ASCORE4,
                                    HSHOTS1,HSHOTS2,HSHOTS3,HSHOTS4,ASHOTS1,ASHOTS2,ASHOTS3,ASHOTS4,HSAVES1,HSAVES2,HSAVES3,HSAVES4,ASAVES1,ASAVES2,ASAVES3,ASAVES4,HPENALTY1,HPENALTY2,HPENALTY3,HPENALTY4,APENALTY1,APENALTY2,APENALTY3,
                                    APENALTY4, HOMEPP, AWAYPP)
                                VALUES
                                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                          (seasonYear, serie, stats[0], stats[1][0:10], stats[2], stats[3], stats[4], stats[5], stats[6],
                           stats[7], stats[8], stats[9], stats[10], stats[11], stats[12], stats[13], stats[14], stats[15],
                           stats[16], stats[17], stats[18], stats[19], stats[20],
                           stats[21], stats[22], stats[23], stats[24], stats[25], stats[26], stats[27], stats[28],
                           stats[29], stats[30], stats[31], stats[32], stats[33], stats[34], stats[35], stats[36],
                           stats[37], stats[38], stats[39], stats[40],
                           stats[41], stats[42], stats[43], stats[44], stats[45]))

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
                                    ID,GAMEID,SEASONID,SERIE,AUDIENCE,VENUE,HOMETEAM,AWAYTEAM,TEAM,GAMEDATE,NUMBER,FORNAME,SURNAME,POSITION,START_PLAYER,
                                    GOALS, PPGOALS, SHGOALS, ASSISTS, PLUS, MINUS, PENALTY, INPOWERPLAY, INBOXPLAY, SHOTSAT, SAVES, SCORE, FINALSCORE, SCORE5, GOALS5, ASSIST5, GAMES5, SCORE_CURRENT, GOALS_CURRENT, ASSIST_CURRENT, GAMES_CURRENT)
                                VALUES
                                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)""",
                              (id, lineups[i][0], lineups[i][9], serie, lineups[i][7], lineups[i][8], stats[2], stats[3], lineups[i][1], stats[1][0:10], lineups[i][2], lineups[i][3], lineups[i][4], lineups[i][5], lineups[i][6]))

                else:
                    pass

                conn.commit()

                c.execute("SELECT PERSONNR from rosters where SEASONID = ? and TEAM = ? and NUMBER = ?",[seasonYear, lineups[i][1], lineups[i][2]])
                personnr = c.fetchall()

                persnr = ''

                if len(personnr) > 0:
                    persnr = personnr[0][0]

                c.execute("UPDATE lineups SET PERSONNR = ? WHERE SEASONID = ? and TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ?",[persnr, seasonYear, lineups[i][1], lineups[i][2], lineups[i][3], lineups[i][4]])

            conn.commit()

            # Get events data from each game
            events = get_actions(gameVector[j][0], audVector[j][0], venueVector[j][0], seasonYear, stats[2], stats[3],c)

            # Create event table
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

                    c.execute(
                        """SELECT PERSONNR FROM rosters WHERE SEASONID = ? and TEAM = ? and NUMBER = ? and FORNAME = ? AND SURNAME = ? """,(seasonYear, events[i][4], events[i][5], events[i][7], events[i][6]))
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
                              (
                              id, events[i][0], events[i][12], events[i][10], events[i][11], events[i][1], events[i][2],
                              events[i][3], events[i][4], events[i][5], pnr, events[i][7], events[i][6], events[i][8],
                              events[i][9]))

                else:
                    pass

            conn.commit()


            # Create ref table
            if serie == "SHL":
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
                                  (stats[0], seasonYear, refs[0], refs[1], stats[2], stats[3], lines[0], lines[1]))

                    else:
                        pass

                conn.commit()


            print(str(stats[0]) + " lineups loaded")



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

                c.execute("SELECT SUM(CASE WHEN EVENT = ? then 1 else 0 end) as X FROM events where GAMEID = ? and TEAM = ? and NUMBER = ? and (extra1 = ? or extra1 = ?)",['-1', gameVector[j][0], lineups[i][0], lineups[i][1], '','PP'])
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


                c.execute("UPDATE lineups SET GOALS = ?, PPGOALS = ?, SHGOALS = ?, ASSISTS = ?, PLUS = ?, MINUS = ?, PENALTY = ?, INPOWERPLAY = ?, INBOXPLAY = ?, SHOTSAT = ?, SAVES = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",
                    [goals, PP, SH, assist, plus, minus, penalty, activePP, activeBP, shotsAt, saves, gameVector[j][0], lineups[i][0], lineups[i][1]])

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

                create_teamgames(seasonYear, serie, c)

            print(str(stats[0]) + " stats, events loaded")
        else:
            print("Game already loaded")

        if t_count == 1:
            t+=1
            print(str(t) + "/" + str(len(gameVector)) + " done")

    #Update score for games

    for j in range(0, len(gameVector)):

        c.execute("SELECT GAMEID FROM TEAMSCORE WHERE GAMEID = ?", [gameVector[j][0]])
        check = c.fetchall()


        if score_update == "Full" or len(check) == 0:

            # Add score to lineups

            c.execute("SELECT TEAM, NUMBER, FORNAME, SURNAME, GAMEDATE, HOMETEAM, AWAYTEAM FROM lineups where GAMEID = ?", [gameVector[j][0]])
            lineups = c.fetchall()

            for i in range(0, len(lineups)):

                c.execute("SELECT * from lineups where GAMEID = ? and TEAM = ? and NUMBER = ?",[gameVector[j][0], lineups[i][0], lineups[i][1]])
                lineup = c.fetchall()

                score = create_game_rating(lineup, lineups[i][0], c,conn)

                if len(score) < 4:
                    score = ['0', '0', '0', '0']

                c.execute(
                    "UPDATE lineups SET SCORE = ?, FINALSCORE = ?, OFFSCORE = ?, DEFSCORE = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",
                    [score[0], score[1], score[2], score[3], gameVector[j][0], lineups[i][0], lineups[i][1]])


            #Calculate team strenght

            if len(lineups) > 0:

                # Check score home team

                [team_strenght, form_score, last_seasons_score, player_score] = calculate_team_strength(lineups[0][5], lineups[0][4], c)

                c.execute("SELECT * FROM TEAMSCORE WHERE GAMEDATE = ? AND TEAM = ?", [lineups[0][4],lineups[0][5]])
                chk = c.fetchall()

                if len(chk) == 0:
                    c.execute("INSERT INTO TEAMSCORE (SEASONID, SERIE, GAMEID, GAMEDATE, TEAM, SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE) VALUES (?,?,?,?,?,?,?,?,?)",
                              [seasonYear, serie, gameVector[j][0],lineups[0][4],lineups[0][5],team_strenght,form_score, last_seasons_score, player_score])
                else:
                    c.execute("UPDATE TEAMSCORE SET SCORE = ?, FORM_SCORE = ?, LAST_SEASONS_SCORE = ?, PLAYER_SCORE = ? WHERE SEASONID = ? AND SERIE = ? AND GAMEID = ? AND TEAM = ?",[team_strenght,form_score, last_seasons_score, player_score, seasonYear, serie, gameVector[j][0],lineups[0][5]])

                #Check score away team

                [team_strenght, form_score, last_seasons_score, player_score] = calculate_team_strength(lineups[0][6], lineups[0][4], c)

                c.execute("SELECT * FROM TEAMSCORE WHERE GAMEDATE = ? AND TEAM = ?", [lineups[0][4], lineups[0][6]])
                chk = c.fetchall()

                if len(chk) == 0:
                    c.execute(
                        "INSERT INTO TEAMSCORE (SEASONID, SERIE, GAMEID, GAMEDATE, TEAM, SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE) VALUES (?,?,?,?,?,?,?,?,?)",
                        [seasonYear, serie, gameVector[j][0], lineups[0][4], lineups[0][6], team_strenght, form_score,last_seasons_score, player_score])
                else:
                    c.execute(
                        "UPDATE TEAMSCORE SET SCORE = ?, FORM_SCORE = ?, LAST_SEASONS_SCORE = ?, PLAYER_SCORE = ? WHERE SEASONID = ? AND SERIE = ? AND GAMEID = ? AND TEAM = ?",
                        [team_strenght, form_score, last_seasons_score, player_score, seasonYear, serie, gameVector[j][0],
                         lineups[0][6]])

            print("Score updated")

            conn.commit()

    # Update pre-game info

    for j in range(0, len(gameVector)):

        c.execute("SELECT GAMEID FROM EXP_SHOTS_TABLE WHERE GAMEID = ?", [gameVector[j][0]])
        check = c.fetchall()

        if 1==1:#len(check) == 0:

            c.execute("SELECT HOMETEAM, AWAYTEAM FROM STATS WHERE GAMEID = ?",[gameVector[j][0]])
            teams = c.fetchall()

            create_pre_match_analysis(dateVector[j][0], serie, teams[0][0], teams[0][1], gameVector[j][0], c, conn)


#scrape_sh(6053, 2016, "HA", "New")
#scrape_sh(5057, 2015, "HA", "New")
#scrape_sh(9168, 2019, "HA", "New")

#scrape_sh(6053, 2016, "HA", "New")
#scrape_sh(5057, 2015, "HA", "New")
#scrape_sh(7132, 2017, "SHL", "New")
#scrape_sh(8121, 2018, "SHL", "New")
scrape_sh(9171, 2019, "SHL", "New")
