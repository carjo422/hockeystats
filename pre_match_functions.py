import numpy as np
from datetime import date

def get_form(team,seasonYear,gamedate,c):
    c.execute("SELECT GAMEDATE, HOMEAWAY, OUTCOME, SCORE11 + SCORE12 + SCORE13 + SCORE14 as SCORE1, SCORE21 + SCORE22 + SCORE23 + SCORE24 as SCORE2, SHOTS1, SHOTS2, PENALTY1, PENALTY2, OPP_SCORE_SIMPLE FROM TEAMGAMES WHERE TEAM = ? and SEASONID = ? AND GAMEDATE < ? ORDER BY GAMEID DESC", [team, seasonYear, gamedate])
    tg = c.fetchall()

    form = 0
    offForm = 0
    defForm = 0
    points5 = 0
    goals5 = 0
    conc5 = 0
    points1 = 0
    goals1 = 0
    conc1 = 0

    df = 0
    n = min(len(tg),5)

    for i in range(0,n):

        gameform = (4 - int(tg[i][2])) / n
        gameOffForm = int(tg[i][3]) / n
        gameDefForm = int(tg[i][4]) / n

        if tg[i][1] == "A":
            gameform *= 1.1
            gameOffForm *= 1.1
            gameDefForm *= 1.1

        gameform *= 3 / (tg[i][9])
        gameOffForm *= 3 / (tg[i][9])
        gameDefForm *= 3 / (tg[i][9])

        form += gameform
        offForm += gameOffForm
        defForm += gameDefForm
        points5 += (4 - int(tg[i][2]))
        goals5 += int(tg[i][3])
        conc5 += int(tg[i][4])

        if i == 0:
            points1 += (4 - int(tg[i][2]))
            goals1 += int(tg[i][3])
            conc5 += int(tg[i][4])

    return [form, offForm, defForm, points5, goals5, conc5, points1, goals1, conc1]

def get_player_form(team,seasonYear,gamedate,c):
    c.execute("SELECT FORNAME, SURNAME, SUM(SCORE)/COUNT(SCORE) AS SCORE, SUM(OFFSCORE)/COUNT(OFFSCORE) AS OFFSCORE, SUM(DEFSCORE)/COUNT(DEFSCORE) AS DEFSCORE, SUM(GOALS) as GOALS, SUM(ASSISTS) as ASSISTS, COUNT(GAMEID) as GAMES FROM LINEUPS WHERE TEAM = ? and SEASONID = ? AND GAMEDATE < ? GROUP BY FORNAME, SURNAME, PERSONNR ORDER BY SCORE DESC",[team,seasonYear,gamedate])
    ln = np.array(c.fetchall())

    return ln

def get_team_schedule(team, seasonYear, gamedate, c):
    c.execute("SELECT GAMEDATE FROM TEAMGAMES WHERE TEAM = ? AND GAMEDATE < ? AND SEASONID = ?", [team, gamedate, seasonYear])
    sc = c.fetchall()

    schedule = 0

    for i in range(0,len(sc)):
        d1 = date(int(gamedate[0:4]),int(gamedate[5:7]),int(gamedate[8:10]))
        d2 = date(int(sc[i][0][0:4]),int(sc[i][0][5:7]),int(sc[i][0][8:10]))

        if (d1-d2).days < 30:
           schedule += 1/(d1-d2).days

    return schedule