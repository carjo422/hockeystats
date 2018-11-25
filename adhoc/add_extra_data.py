import datetime
import sqlite3
import urllib.request as urllib

from scfiles.get_stats import get_stats
from scfiles.official_roster import get_official_roster

from calcFunctions import create_teamgames
from functions import get_td_content
from functions import isnumber
from scfiles.get_year_statistics import get_year_statistics

conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

def add_rosters(seasonID, seasonYear, serie):

    rosters = get_official_roster(seasonID, seasonYear, serie)
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

    # Add roster statistics
    get_year_statistics(seasonID, seasonYear, serie)

    c.execute(
        "SELECT GAMEDATE, SERIE, HOMETEAM, AWAYTEAM, GAMEID FROM stats WHERE (SEASONID = ? OR SEASONID = ?) AND SERIE = ? ORDER BY GAMEID",
        [2018, 2019, 'SHL'])
    games = c.fetchall()

    print(games)

    count = 0

    for i in range(0, len(games)):
        count += 1

        gamedate = games[i][0]
        serie = games[i][1]
        hometeam = games[i][2]
        awayteam = games[i][3]
        gameid = games[i][4]

        create_pre_match_analysis(gamedate, serie, hometeam, awayteam, gameid, c, conn)

        print(count, "/", len(games))


def add_team_games(seasonID, seasonYear, serie):

    scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)

    gameVector = []
    venueVector = []
    audVector = []
    dateVector = []

    response = urllib.urlopen(scheduleUrl)
    page_source = str(response.read())

    import sqlite3
    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()

    # Check if vectors exist
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

        for i in range(1, len(page_source) - 10):

            if isnumber(page_source[i:i + 4]) and page_source[i + 4] == '-' and isnumber(page_source[i + 5:i + 7]) and \
                    page_source[i + 7] and isnumber(page_source[i + 8:i + 10]):
                dateVector.append(page_source[i:i + 11])

            if page_source[i:i + 8] == "/Events/":

                gameID = 0

                for j in range(1, 10):
                    if isnumber(page_source[i + 8 + j]) == False:
                        if gameID == 0:
                            gameID = page_source[i + 8:i + 8 + j]
                            gameVector.append(gameID)

                audience = ""

                tds = get_td_content(page_source[i:max(len(page_source) - 10, i + 200)])

                inserted = 0

                for j in range(0, 10):
                    if isnumber(tds[j]) and inserted == 0:
                        inserted = 1
                        audVector.append(int(tds[j]))
                        venueVector.append(tds[j + 1])

        for j in range(0, len(gameVector)):
            c.execute("INSERT INTO schedule (SEASONID, SERIE, GAMEID, GAMEDATE, AUD, VENUE) VALUES (?,?,?,?,?,?)",
                      [seasonYear, serie, gameVector[j], dateVector[j + 1], audVector[j], venueVector[j]])

        c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        gameVector = c.fetchall()
        c.execute("SELECT GAMEDATE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        dateVector = c.fetchall()
        c.execute("SELECT AUD from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        audVector = c.fetchall()
        c.execute("SELECT VENUE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        venueVector = c.fetchall()

    else:

        c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        gameVector = c.fetchall()
        c.execute("SELECT GAMEDATE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        dateVector = c.fetchall()
        c.execute("SELECT AUD from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        audVector = c.fetchall()
        c.execute("SELECT VENUE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
        venueVector = c.fetchall()


    for j in range(0, len(gameVector)):
        stats = get_stats(gameVector[j][0], dateVector[j][0])

        c.execute("SELECT GAMEID as GAMEID FROM stats where GAMEID = ?",[stats[0]])

        hits = c.fetchall()

        if len(hits) == 0:

            c.execute("""INSERT INTO
                            stats (
                                SEASONID,SERIE,GAMEID,GAMEDATE,HOMETEAM,AWAYTEAM,HOMESCORE,AWAYSCORE,HOMESHOTS,AWAYSHOTS,HOMESAVES,AWAYSAVES,HOMEPENALTY,AWAYPENALTY,HSCORE1,HSCORE2,HSCORE3,HSCORE4,ASCORE1,ASCORE2,ASCORE3,ASCORE4,
                                HSHOTS1,HSHOTS2,HSHOTS3,HSHOTS4,ASHOTS1,ASHOTS2,ASHOTS3,ASHOTS4,HSAVES1,HSAVES2,HSAVES3,HSAVES4,ASAVES1,ASAVES2,ASAVES3,ASAVES4,HPENALTY1,HPENALTY2,HPENALTY3,HPENALTY4,APENALTY1,APENALTY2,APENALTY3,
                                APENALTY4)
                            VALUES
                                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                      (
                      seasonYear, serie, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7],
                      stats[8], stats[9], stats[10], stats[11], stats[12], stats[13], stats[14], stats[15], stats[16],
                      stats[17], stats[18], stats[19], stats[20],
                      stats[21], stats[22], stats[23], stats[24], stats[25], stats[26], stats[27], stats[28], stats[29],
                      stats[30], stats[31], stats[32], stats[33], stats[34], stats[35], stats[36], stats[37], stats[38],
                      stats[39], stats[40],
                      stats[41], stats[42], stats[43]))

        else:
            pass

    conn.commit()

    create_teamgames(seasonYear, serie)


c.execute("DELETE FROM rosters where seasonID = ? and serie = ?",['2019','SHL'])
c.execute("DELETE FROM schedule where seasonID = ? and serie = ?",['2019','SHL'])
c.execute("DELETE FROM teamgames where seasonID = ? and serie = ?",['2019','SHL'])
c.execute("DELETE FROM lineups where seasonID = ? and serie = ?",['2019','SHL'])
c.execute("DELETE FROM events where seasonID = ?",['2019'])
c.execute("DELETE FROM stats where seasonID = ?",['2019'])
conn.commit()

#c.execute("UPDATE lineups SET GAMEDATE = SUBSTR(GAMEDATE,1,10)")
#c.execute("UPDATE teamgames SET GAMEDATE = SUBSTR(GAMEDATE,1,10)")
#c.execute("UPDATE stats SET GAMEDATE = SUBSTR(GAMEDATE,1,10)")
#c.execute("UPDATE schedule SET GAMEDATE = SUBSTR(GAMEDATE,1,10)")
#conn.commit()

#add_team_games(2892, 2013, "SHL")
#add_team_games(3905, 2014, "SHL")
#add_team_games(5056, 2015, "SHL")


#add_rosters(2892, 2013, "SHL")
#add_rosters(3905, 2014, "SHL")
#add_rosters(5056, 2015, "SHL")


#add_team_games(8122, 2018, "HA")
#add_team_games(7157, 2017, "HA")
#add_team_games(6053, 2016, "HA")
#add_team_games(5057, 2015, "HA")
#add_team_games(3906, 2014, "HA")
#add_team_games(3005, 2013, "HA")


#add_rosters(8122, 2018, "HA")
#add_rosters(7157, 2017, "HA")
#add_rosters(6053, 2016, "HA")
#add_rosters(5057, 2015, "HA")
#add_rosters(3906, 2014, "HA")
#add_rosters(3005, 2013, "HA")


