#def get_year_statistics(seasonID, season, serie):

#test = get_official_roster(9006, 2018, 'SM Slutspel')

import urllib.request as urllib

from functions import get_td_content
from functions import isnumber


def get_year_statistics(id,seasonYear,serie):

    gameUrl = "http://stats.swehockey.se/Teams/Info/PlayersByTeam/" + str(id)
    response = urllib.urlopen(gameUrl)
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

    tds = get_td_content(page_source)

    import sqlite3
    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()

    c.execute("SELECT DISTINCT TEAM FROM rosters where seasonid = ? and serie = ?", [seasonYear, serie])
    teams = c.fetchall()



    for j in range(0,len(teams)):

        last_n = 0
        search_keepers = 0

        team_found = 0

        for i in range(0,len(tds)):
            if teams[j][0] in tds[i]:
                team_found += 1

                if team_found == 2:
                    team = tds[i]

            if "," in tds[i] and tds[i+1] in ["GK","LD","RD","LW","RW","CE"]:

                forname = tds[i][tds[i].find(",")+2:len(tds[i])]
                forname = forname.replace("*","")

                surname = tds[i][0:tds[i].find(",")]

                games = tds[i+2]
                goals = tds[i+3]
                assist = tds[i+4]
                penalty = tds[i+6]
                plus = tds[i+7]
                minus = tds[i+8]
                shots = 0
                saves = 0

                c.execute("UPDATE rosters SET GAMES = ?, GOALS = ?, ASSIST = ?, PENALTY = ?, PLUS = ?, MINUS = ?, SHOTS = ?, SAVES = ? WHERE SEASONID = ? and SERIE = ? and TEAM = ? and FORNAME = ? and SURNAME = ?",[games, goals, assist, penalty, plus, minus, shots, saves, seasonYear, serie, team, forname, surname])
                conn.commit()

            if isnumber(tds[i]) and isnumber(tds[i + 1]) == True and "," in tds[i + 2]:

                if last_n > int(tds[i]):

                    if search_keepers == 0:
                        search_keepers = 1
                    else:
                        search_keepers = 0

                last_n = int(tds[i])

                if search_keepers == 1:
                    if ":" in tds[i + 6]:

                        forname = tds[i+2][tds[i+2].find(",") + 2:len(tds[i+2])]
                        forname = forname.replace("*", "")

                        surname = tds[i+2][0:tds[i+2].find(",")]

                        games = tds[i+5]
                        goals = 0
                        assist = 0
                        penalty = 0
                        plus = 0
                        minus = 0
                        shots = tds[i+9]
                        saves = tds[i+8]

                        c.execute("UPDATE rosters SET GAMES = ?, SHOTS = ?, SAVES = ? WHERE SEASONID = ? and SERIE = ? and TEAM = ? and FORNAME = ? and SURNAME = ?",
                            [games, shots, saves, seasonYear, serie, team, forname,
                             surname])

                        conn.commit()



