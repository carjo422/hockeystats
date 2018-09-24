from official_roster import get_official_roster
import datetime
from get_year_statistics import get_year_statistics

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
    pass

add_team_games(2892, 2013, "SHL")
add_team_games(3905, 2014, "SHL")
add_team_games(5056, 2015, "SHL")


add_rosters(2892, 2013, "SHL")
add_rosters(3905, 2014, "SHL")
add_rosters(5056, 2015, "SHL")