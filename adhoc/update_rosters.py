########################################################################################################################
##########################################    Get aggregated statistics    #############################################
########################################################################################################################

from scfiles.official_roster import get_official_roster
from scfiles.get_year_statistics import get_year_statistics
from functions import isnumber
import datetime
import sqlite3


conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
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

    #Add score to rosters
    c.execute("SELECT FORNAME, SURNAME, PERSONNR, POSITION, GAMES, GOALS, ASSIST, PENALTY, PLUS, MINUS, SHOTS, SAVES FROM ROSTERS WHERE SEASONID = ? AND SERIE = ?",[seasonYear,serie])
    re_score = c.fetchall()

    divFact = 1

    if serie == 'HA':
        divFact = 0.5

    for i in range(0,len(re_score)):

        if re_score[i][4] != None:

            if re_score[i][4] != 0:

                if re_score[i][3] in ['LD','RD']:
                    roster_score = (re_score[i][4]*8+re_score[i][5]*12+re_score[i][6]*8-re_score[i][7]*2+re_score[i][8]*8-re_score[i][9]*8) / re_score[i][4]*divFact

                elif re_score[i][3] in ['CE', 'RW', 'LW']:
                    roster_score = (re_score[i][4] * 5 + re_score[i][5] * 12 + re_score[i][6] * 8 - re_score[i][7] * 4 + re_score[i][8] * 8 - re_score[i][9] * 8) / re_score[i][4]*divFact

                else:
                    roster_score = (re_score[i][10] * 2.6 + (re_score[i][10] - re_score[i][11]) * -20) / re_score[i][4]*divFact

            else:
                roster_score = 0

        else:
            roster_score = 0

        roster_score_final = roster_score # TEMPORARY SOLUTION

        c.execute("UPDATE ROSTERS SET ROSTER_SCORE = ?, ROSTER_SCORE_FINAL = ? WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND SEASONID = ?",[roster_score, roster_score_final, re_score[i][0], re_score[i][1], re_score[i][2], seasonYear])

    conn.commit()

    #Fix score_final

    c.execute("SELECT SEASONID, TEAM, SUM(PLUS-MINUS) AS TSCORE FROM ROSTERS WHERE SEASONID = ? AND SERIE = ? AND POSITION != ? GROUP BY SEASONID, TEAM ORDER BY TSCORE",[seasonYear,serie, 'GK'])
    ave_score = c.fetchall()

    print(ave_score)

    max_value = ave_score[len(ave_score) - 1][2]
    min_value = ave_score[0][2]

    span = max_value - min_value



    for i in range(0,len(ave_score)):
        #team_adjust.append([ave_score[i][1],(ave_score[i][2]/span)*0.55])

        c.execute("SELECT SEASONID, TEAM, FORNAME, SURNAME, PERSONNR, ROSTER_SCORE FROM ROSTERS WHERE SEASONID = ? AND TEAM = ?",[seasonYear, ave_score[i][1]])
        player_list = c.fetchall()

        for j in range(0,len(player_list)):
            c.execute("UPDATE ROSTERS SET ROSTER_SCORE_FINAL = ? WHERE SEASONID = ? AND TEAM = ? AND FORNAME = ? AND SURNAME = ? AND PERSONNR = ?", [((ave_score[i][2] / span) * 0.55+1) * player_list[j][5], seasonYear, player_list[j][1],player_list[j][2],player_list[j][3],player_list[j][4]])
            (ave_score[i][2] / span) * 0.55

    conn.commit()

    print(str(seasonYear) + " " + serie + " roster updated")

#update_rosters(3905, 2014, 'SHL')
update_rosters(5056, 2015, 'SHL')
update_rosters(6052, 2016, 'SHL')
update_rosters(7132, 2017, 'SHL')
update_rosters(8121, 2018, 'SHL')
update_rosters(9171, 2019, 'SHL')

#update_rosters(3906, 2014, 'HA')
update_rosters(5057, 2015, 'HA')
update_rosters(6053, 2016, 'HA')
update_rosters(7157, 2017, 'HA')
update_rosters(8122, 2018, 'HA')
update_rosters(9168, 2019, 'HA')