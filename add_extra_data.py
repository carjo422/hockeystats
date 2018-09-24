from official_roster import get_official_roster
import datetime
from get_year_statistics import get_year_statistics
from calcFunctions import create_teamgames
import urllib.request as urllib
from functions import isnumber
from functions import get_td_content
from get_stats import get_stats

import sqlite3
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

    conn.commit()

    stats = get_stats(gameVector[j][0], dateVector[j][0])

    print(stats)

    #create_teamgames(seasonYear, serie)

add_team_games(2892, 2013, "SHL")
add_team_games(3905, 2014, "SHL")
add_team_games(5056, 2015, "SHL")


add_rosters(2892, 2013, "SHL")
add_rosters(3905, 2014, "SHL")
add_rosters(5056, 2015, "SHL")