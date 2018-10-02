import numpy as np
from datetime import date
from scipy.stats import poisson

def get_form(team,seasonYear,gamedate,c):
    c.execute("SELECT GAMEDATE, HOMEAWAY, OUTCOME, SCORE11 + SCORE12 + SCORE13 + SCORE14 as SCORE1, SCORE21 + SCORE22 + SCORE23 + SCORE24 as SCORE2, SHOTS1, SHOTS2, PENALTY1, PENALTY2, OPP_SCORE_SIMPLE FROM TEAMGAMES WHERE TEAM = ? and SEASONID = ? AND GAMEDATE < ? ORDER BY GAMEID DESC", [team, seasonYear, gamedate])
    tg = c.fetchall()

    form = 0
    offForm = 0
    defForm = 0
    points5 = 0
    goals5 = 0
    conc5 = 0
    points3 = 0
    goals3 = 0
    conc3 = 0
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
            conc1 += int(tg[i][4])

        if i < 3:
            points3 += (4 - int(tg[i][2]))
            goals3 += int(tg[i][3])
            conc3 += int(tg[i][4])

    return [form, offForm, defForm, points5, goals5, conc5, points3, goals3, conc3, points1, goals1, conc1]

def get_player_form(team,seasonYear,gamedate,c):

    c.execute("SELECT GAMEID FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? ORDER BY GAMEDATE",[team, seasonYear])
    gdt = c.fetchall()
    lastgame = gdt[0][0]

    c.execute("SELECT FORNAME, SURNAME, SUM(SCORE)/COUNT(SCORE) AS SCORE, SUM(OFFSCORE)/COUNT(OFFSCORE) AS OFFSCORE, SUM(DEFSCORE)/COUNT(DEFSCORE) AS DEFSCORE, SUM(GOALS) as GOALS, SUM(ASSISTS) as ASSISTS, COUNT(GAMEID) as GAMES FROM LINEUPS WHERE TEAM = ? and SEASONID = ? AND GAMEDATE < ? GROUP BY FORNAME, SURNAME, PERSONNR ORDER BY SCORE DESC",[team,seasonYear,gamedate])
    fss = np.array(c.fetchall())

    c.execute("SELECT FORNAME, SURNAME, GOALS, ASSISTS, PLUS, MINUS FROM LINEUPS WHERE TEAM = ? and SEASONID = ? and GAMEID = ? ORDER BY GAMEDATE DESC",[team, seasonYear, lastgame])
    lgs = np.array(c.fetchall())

    return [fss, lgs]



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

def getOdds1X2(homeScore,awayScore):

    vect1 = [0.21, 0.245, 0.305, 0.365, 0.425, 0.485, 0.545, 0.635, 0.705, 0.77, 0.85]
    vect2 = [0.7, 0.65, 0.55, 0.44, 0.35, 0.28, 0.22, 0.15, 0.12, 0.10, 0.06]
    vectX = [0.09, 0.105, 0.145, 0.195, 0.225, 0.235, 0.235, 0.215, 0.175, 0.13, 0.09]

    vectB = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]

    ratio = homeScore / awayScore

    if ratio < 0.2:
        ratio = 0.2

    if ratio > 2.2:
        ratio = 2.2

    for i in range(0,10):
        if ratio >= vectB[i] and ratio <= vectB[i+1]:

            fact = (ratio-vectB[i])/(vectB[i+1]-vectB[i])

            odds1 = vect1[i+1]*fact+vect1[i]*(1-fact)
            oddsX = vectX[i+1]*fact+vectX[i]*(1-fact)
            odds2 = vect2[i+1]*fact+vect2[i]*(1-fact)

    return [odds1, oddsX, odds2]



def getOdds55(offForm1, defForm1, offForm2, defForm2):

    exp_score = offForm1/2 + offForm2/2 + defForm1/2 + defForm2/2

    prob4 = poisson.cdf(4, exp_score)
    prob5 = poisson.cdf(4, exp_score)
    prob6 = poisson.cdf(4, exp_score)

    return [prob4, prob5, prob6]



def get_offence_info(team, offForm, goals5, goals3, goals1, fss, lgs):

    line1=""
    line2=""

    print(lgs)

    if offForm > 3.5:
        line1 = team + " har öst in mål senaste matcherna."
        line1 = team + " har bra fart på målskyttet."

        if goals1 == 0:
            line2 = "Senast blev man dock nollade mot okänd motståndare"
        elif goals1 == 1:
            line2 = "Dock bara ett mål senast mot okänd motståndare"
        elif goals1 > 1 and goals1 < 5:
            line2 = str(goals1) + " mål senast mot okänd motståndare"
        else:
            line2 = "Hela " + str(goals1) + " mål senast mot okänd motståndare"


    elif offForm > 3:
        line1 = "Stark offensiv för " + team + "."
        line1 = team + " har bra fart på målskyttet."

        if goals1 == 0:
            line2 = "Senast blev man dock nollade mot okänd motståndare"
        elif goals1 == 1:
            line2 = "Dock bara ett mål senast mot okänd motståndare"
        elif goals1 > 1 and goals1 < 5:
            line2 = str(goals1) + " mål senast mot okänd motståndare"
        else:
            line2 = "Hela " + str(goals1) + " mål senast mot okänd motståndare"


    elif offForm > 2.5:
        line1 = "Offensiven ser hyfsad ut för " + team + ""

        if goals1 == 0:
            line2 = "Nollade senast mot okänd motståndare."
        elif goals1 == 1:
            line2 = "Bara ett mål senast mot okänd motståndare."
        elif goals1 > 1 and goals1 < 5:
            line2 = str(goals1) + " mål senast mot okänd motståndare"
        else:
            line2 = "Hela " + str(goals1) + " mål senast mot okänd motståndare"


    elif offForm > 2.0:
        line1 = team + " har problem med målskyttet."
        line1 = team + " har inte fått offensiven att fungera."

        if goals1 == 0:
            line2 = "Nollade senast mot okänd motståndare."
        elif goals1 == 1:
            line2 = "Bara ett mål senast mot okänd motståndare."
        elif goals1 > 2:
            line2 = str(goals1) + " mål senast mot okänd motståndare var dock ett steg i rätt riktning."
        else:
            line2 = ""


    print(line1, line2)

    return line1

pass