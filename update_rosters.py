########################################################################################################################
##########################################    Get aggregated statistics    #############################################
########################################################################################################################

from scfiles.official_roster import get_official_roster
from scfiles.get_year_statistics import get_year_statistics
import datetime
import sqlite3


conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()


def update_rosters(seasonID,seasonYear,serie):

    #Get the seasons roster
    rosters = get_official_roster(seasonID,seasonYear,serie)

    # Create roster table in database
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


    #Add statistics to roster
    get_year_statistics(seasonID, seasonYear, serie)

    print(str(seasonYear) + " " + serie + " roster updated")

#update_rosters(3905, 2014, 'SHL')
#update_rosters(5056, 2015, 'SHL')
#update_rosters(6052, 2016, 'SHL')
#update_rosters(7132, 2017, 'SHL')
#update_rosters(8121, 2018, 'SHL')
#update_rosters(9171, 2019, 'SHL')

update_rosters(3906, 2014, 'HA')
update_rosters(5057, 2015, 'HA')
update_rosters(6053, 2016, 'HA')
update_rosters(7157, 2017, 'HA')
update_rosters(8122, 2018, 'HA')
update_rosters(9168, 2019, 'HA')