import numpy as np
from datetime import date
from scipy.stats import poisson
from functions import transform_date

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

    return [form, offForm, defForm, points5, goals5, conc5, points3, goals3, conc3, points1, goals1, conc1, n]

def get_strength(team, seasonYear, gamedate, c):

    c.execute("SELECT GAMEID FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? ORDER BY GAMEDATE DESC", [team, seasonYear])
    gdt = c.fetchall()
    lastgame = gdt[0][0]

    c.execute("SELECT a.gameid, a.seasonid, a.gamedate, a.forname, a.surname, a.position as line, b.position, a.goals, a.assists, a.plus, a.minus, a.penalty, a.shotsat, c.player_score, c.roster_score, c.lineup_score, c.TWL, c.TWR from lineups a left join rosters b on a.seasonid = b.seasonid and a.personnr = b.personnr and a.forname = b.forname left join team_score_build c on a.gamedate = c.gamedate and a.personnr = c.personnr and a.forname = c.forname where a.seasonid = ? and a.team = ? and a.gameid = ?",[seasonYear, team, lastgame])
    lineup = c.fetchall()


    team_strength = 0
    off_strength = 0
    def_strength = 0

    w1=0
    w2=0
    w3=0

    for i in range(0,len(lineup)):
        if lineup[i][5] == "Goalies":
            w1 += 30
            w3 += 15

            team_strength+= lineup[i][13]*30
            def_strength+= lineup[i][13]*15

        elif lineup[i][5] == "1st Line":
            w1 += 5
            w2 += 5
            w3 += 5

            team_strength += lineup[i][13] * 5
            off_strength += lineup[i][13] * 5
            def_strength += lineup[i][13] * 5

        elif lineup[i][5] == "2nd Line":
            w1 += 3
            w2 += 3
            w3 += 3

            team_strength += lineup[i][13] * 3
            off_strength += lineup[i][13] * 3
            def_strength += lineup[i][13] * 3

        elif lineup[i][5] == "3rd Line":
            w1 += 2
            w2 += 2
            w3 += 2

            team_strength += lineup[i][13] * 2
            off_strength += lineup[i][13] * 2
            def_strength += lineup[i][13] * 2

        elif lineup[i][5] == "4th Line":
            w1 += 1
            w2 += 1
            w3 += 1

            team_strength += lineup[i][13] * 1
            off_strength += lineup[i][13] * 1
            def_strength += lineup[i][13] * 1

    team_strength /= w1
    off_strength /= w2
    def_strength /= w3

    return [team_strength, off_strength, def_strength]


def get_player_form(team,seasonYear,gamedate,c):

    c.execute("SELECT GAMEID FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? ORDER BY GAMEDATE DESC",[team, seasonYear])
    gdt = c.fetchall()
    lastgame = gdt[0][0]

    c.execute("""SELECT FORNAME, SURNAME, SUM(SCORE)/COUNT(SCORE) AS SCORE, SUM(OFFSCORE)/COUNT(OFFSCORE) AS OFFSCORE, SUM(DEFSCORE)/COUNT(DEFSCORE) AS DEFSCORE, SUM(GOALS) as GOALS, SUM(ASSISTS) as ASSISTS, COUNT(GAMEID) as GAMES FROM LINEUPS WHERE TEAM = ? and SEASONID = ? AND GAMEDATE < ? GROUP BY FORNAME, SURNAME, PERSONNR ORDER BY SCORE DESC""",[team,seasonYear,gamedate])
    players = c.fetchall()

    olddate = transform_date(gamedate,20)

    c.execute("""SELECT FORNAME, SURNAME, SUM(SCORE)/COUNT(SCORE) AS SCORE, SUM(OFFSCORE)/COUNT(OFFSCORE) AS OFFSCORE, SUM(DEFSCORE)/COUNT(DEFSCORE) AS DEFSCORE, SUM(GOALS) as GOALS, SUM(ASSISTS) as ASSISTS, COUNT(GAMEID) as GAMES FROM LINEUPS WHERE TEAM = ? and SEASONID = ? AND GAMEDATE < ? AND GAMEDATE > ? GROUP BY FORNAME, SURNAME, PERSONNR ORDER BY SCORE DESC""",[team, seasonYear, gamedate, olddate])
    players5 = c.fetchall()

    c.execute("SELECT FORNAME, SURNAME, GOALS, ASSISTS, PLUS, MINUS, POSITION FROM LINEUPS WHERE TEAM = ? and SEASONID = ? and GAMEID = ? ORDER BY GAMEDATE DESC",[team, seasonYear, lastgame])
    players1 = c.fetchall()

    return [players, players1, players5]

def get_stats(team, seasonYear, gamedate, c):

    c.execute("SELECT * FROM teamgames where TEAM = ? and gamedate = ?", [team, gamedate])
    stats1 = c.fetchall()

    return stats1[0]



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
    prob5 = poisson.cdf(5, exp_score)
    prob6 = poisson.cdf(6, exp_score)

    return [prob4, prob5, prob6]

def create_tables(seasonYear, serie, c):


    #Standings table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(CASE WHEN OUTCOME = 1 then 1 else 0 end) as WINS, SUM(CASE WHEN OUTCOME = 2 then 1 else 0 end) as OT_WINS, SUM(CASE WHEN OUTCOME = 3 then 1 else 0 end) as OT_LOSS,
                 SUM(CASE WHEN OUTCOME = 4 then 1 else 0 end) as LOSS,  SUM(CASE WHEN OUTCOME = 1 then 3 WHEN OUTCOME = 2 then 2 WHEN OUTCOME = 1 then 1 else 0 end) as POINTS, SUM(SCORE1) as G, SUM(SCORE2) as C,
                 SUM(SCORE1)-SUM(SCORE2) as D FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY POINTS DESC, D DESC, G DESC""",[str(seasonYear),serie])

    full_table = c.fetchall()

    #Home table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(CASE WHEN OUTCOME = 1 then 1 else 0 end) as WINS, SUM(CASE WHEN OUTCOME = 2 then 1 else 0 end) as OT_WINS, SUM(CASE WHEN OUTCOME = 3 then 1 else 0 end) as OT_LOSS,
        SUM(CASE WHEN OUTCOME = 4 then 1 else 0 end) as LOSS,  SUM(CASE WHEN OUTCOME = 1 then 3 WHEN OUTCOME = 2 then 2 WHEN OUTCOME = 1 then 1 else 0 end) as POINTS, SUM(SCORE1) as G, SUM(SCORE2) as C,
        SUM(SCORE1)-SUM(SCORE2) as D FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? AND HOMEAWAY = ? GROUP BY TEAM ORDER BY POINTS DESC, D DESC, G DESC""",
              [str(seasonYear), serie,"H"])

    home_table = c.fetchall()

    #Away table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(CASE WHEN OUTCOME = 1 then 1 else 0 end) as WINS, SUM(CASE WHEN OUTCOME = 2 then 1 else 0 end) as OT_WINS, SUM(CASE WHEN OUTCOME = 3 then 1 else 0 end) as OT_LOSS,
        SUM(CASE WHEN OUTCOME = 4 then 1 else 0 end) as LOSS,  SUM(CASE WHEN OUTCOME = 1 then 3 WHEN OUTCOME = 2 then 2 WHEN OUTCOME = 1 then 1 else 0 end) as POINTS, SUM(SCORE1) as G, SUM(SCORE2) as C,
        SUM(SCORE1)-SUM(SCORE2) as D FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? AND HOMEAWAY = ? GROUP BY TEAM ORDER BY POINTS DESC, D DESC, G DESC""",
              [str(seasonYear), serie,"A"])

    away_table = c.fetchall()

    #Scoring table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(SCORE1) as X, SUM(SCORE1)/COUNT(TEAM) as AX FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY AX DESC""",[str(seasonYear), serie])

    score_table = c.fetchall()

    #Conciding table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(SCORE2) as X, SUM(SCORE2)/COUNT(TEAM) as AX FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY AX DESC""",[str(seasonYear), serie])

    con_table = c.fetchall()

    #Shots table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(SHOTS1) as X, SUM(SHOTS1)/COUNT(TEAM) as AX FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY AX DESC""",[str(seasonYear), serie])

    shots_table = c.fetchall()

    #Penalty table

    c.execute("""SELECT TEAM, COUNT(TEAM) as MATCHES, SUM(PENALTY1) as X, SUM(PENALTY1)/COUNT(TEAM) as AX FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY AX DESC""",[str(seasonYear), serie])

    penalty_table = c.fetchall()

    #Powerplay goals table

    c.execute("""SELECT a.TEAM, SUM(a.PPGOALS) as PPGOALS FROM lineups a where a.SEASONID = ? AND a.SERIE = ? GROUP BY a.TEAM ORDER BY TEAM""",[str(seasonYear), serie])

    pp_table = c.fetchall()

    # Powerplay % table

    c.execute("""SELECT TEAM, SUM(PENALTY2) as PP FROM TEAMGAMES where SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY TEAM""",[str(seasonYear), serie])

    standings = c.fetchall()
    pp_percent_table = []
    for i in range(0,len(standings)):
        pp_percent_table.append([pp_table[i][0],pp_table[i][1] / standings[i][1]*2])

    return [full_table, home_table, away_table, score_table, con_table, shots_table, penalty_table, pp_table, pp_percent_table]

def get_table_info(team, table, t, b):

    if t == 10:

        v = 0
        for i in range(0, len(table)):
            if table[i][0] == team:
                p = i+1

    else:

        for i in range(0,len(table)):
            if table[i][0] == team:
                v = table[i][t]


        p=b
        if b == 1:
            for i in range(0,len(table)):
                if table[i][t] > v:
                    p +=1
        if b == 0:
            for i in range(0, len(table)):
                if table[i][t] >= v:
                    p += 1

        return [v,p]


def get_offence_info(team, offForm, offStrenght, goals5, goals3, goals1, players, players1, players5, stats1, n_matches5, score_table, shots_table, pp_table, pp_percent_table):

    line = ["","","","","","","","","",""]

    [score_n, score_p] = get_table_info(team, score_table, 2, 1)
    [match_n, match_p] = get_table_info(team, score_table, 1, 1)

    last_opponent = stats1[6]

    if stats1[7] in [1, 2]:
        last_outcome = "Vinst"
    else:
        last_outcome = "Förlust"

    goal_scorers = []

    for i in range(0, len(players1)):
        if players1[i][2] > 0:
            goal_scorers.append(players1[i])

    best_scorers = []

    max_goals=0
    for i in range(0, len(players)):
        if players[i][5] > max_goals:
            max_goals = players[i][5]

    for i in range(0, len(players)):
        if players[i][5] >= max_goals*0.75:
            best_scorers.append([players[i][0], players[i][1], players[i][5]])


    if n_matches5 > 2:

        if score_p == 1:
            line[0] = team + " har gjort flest mål i SHL hittills, " + str(score_n) + " på " + str(match_n) + " matcher. "
        if score_p == 2:
            line[0] = team + " har gjort näst flest mål i SHL hittills, " + str(score_n) + " på " + str(match_n) + " matcher. "
        if score_p == len(score_table):
            line[0] = team + " har gjort minst mål i SHL hittills, bara " + str(score_n) + " på " + str(match_n) + " matcher. "
        if score_p == len(score_table)-1:
            line[0] = team + " har gjort näst minst mål i SHL hittills, bara " + str(score_n) + " på " + str(match_n) + " matcher. "

        if offForm > 3.5:
            if line[0] == "":
                line[1] = team + " har öst in mål senaste matcherna, " + str(goals5) + " mål på de " + str(n_matches5) + " senaste. "
            else:
                pass#line[1] = str(goals5) + " mål på de " + str(n_matches5) + " senaste matcherna. "

        elif offForm > 3:
            if line[0] == "":
                line[1] = team + " har för tillfället en välfungerande offensiv, " + str(goals5) + " mål på de " + str(n_matches5) + " senaste. "
            else:
                line[1] = str(goals5) + " mål på de " + str(n_matches5) + " senaste matcherna. "

        elif offForm > 2.5:
            if line[0] == "":
                line[1] = team + " har gjort " + str(goals5) + " mål på de " + str(n_matches5) + " senaste. "
            else:
                line[1] = str(goals5) + " mål på de " + str(n_matches5) + " senaste matcherna. "

        elif offForm > 0:
            if line[0] == "":
                line[1] = team + " har problem med målskyttet, bara " + str(goals5) + " mål på de " + str(n_matches5) + " senaste. "
            else:
                line[1] = "Bara " + str(goals5) + " mål på de " + str(n_matches5) + " senaste matcherna. "

        if offForm > 3.0:
            if goals1 == 0:
                line[2] = "Sist blev man dock nollade mot " + last_opponent
            elif goals1 == 1:
                line[2] = "Dock bara ett senast mot " + last_opponent
            elif goals1 > 1 and goals1 < 5:
                line[2] = str(goals1) + " senast mot " + last_opponent
            else:
                line[2] = "Hela " + str(goals1) + " mål senast mot " + last_opponent
        else:
            if goals1 == 0:
                line[2] = "Man blev nollade senast mot " + last_opponent
            elif goals1 == 1:
                line[2] = "Bara 1 senast mot " + last_opponent
            elif goals1 > 3:
                line[2] = "" + str(goals1) + " mål senast " + last_opponent + " var dock ett steg i rätt riktning."
            else:
                line[2] = str(goals1) + " senast mot " + last_opponent

        if "." in line[2]:
            if goals1 == 0:
                pass
            elif goals1 == 1:
                line[3] = " Målskytt senast var, "
            elif goals1 > 1:
                line[3] = " Målskyttar senast var, "
        else:
            if goals1 == 0:
                pass
            else:
                line[3] = " efter mål av "

        if goals1 > 0:
            for i in range(0,len(goal_scorers)):

                ext = ""
                if goal_scorers[i][2] > 1:
                    ext = "(" + str(goal_scorers[i][2]) + ")"

                if i < len(goal_scorers)-2:
                    line[3] = line[3] + goal_scorers[i][1] + ext + ", "
                elif i == len(goal_scorers)-2:
                    line[3] = line[3] + goal_scorers[i][1] + ext + " och "
                else:
                    line[3] = line[3] + goal_scorers[i][1] + ext + ". "


    if match_n < 6:
        goal_comment = "."
    elif match_n < 11:
        goal_comment = "."
    elif match_n < 16:
        goal_comment = "."


    if len(best_scorers) > 0:
        if len(best_scorers) > 1:
            if best_scorers[0][2] > 1:
                line[4] = "Bästa målskyttar "
                for i in range(0,len(best_scorers)):
                    if i < len(best_scorers)-1:
                        line[4] = line[4] + best_scorers[i][0] + " " + str(best_scorers[i][1]) + " (" + str(best_scorers[i][2]) + "), "
                    else:
                        line[4] = line[4] + best_scorers[i][0] + " " + str(best_scorers[i][1]) + " (" + str(best_scorers[i][2]) + ")" + goal_comment
        else:
            if best_scorers[0][2] > 1:
                line[4] = "Bästa målskytt "
                for i in range(0, len(best_scorers)):
                    line[4] = line[4] + best_scorers[i][0] + " " + str(best_scorers[i][1]) + " på "

                line[4] = line[4] + str(best_scorers[0][2]) + "."

    print(line[0] + line[1] + line[2] + line[3] + line[4])

    return line

def get_defence_info(team, opp, defStrenght, con1, players, players1, players5, stats1, n_matches5, con_table, penalty_table, pp_percent_table):

    # Establish connection to database
    import sqlite3
    conn = sqlite3.connect('hockeystats.db')
    c = conn.cursor()

    line = ["","","","","","","","","",""]

    [con_n, con_p] = get_table_info(team, con_table, 2, 0)
    [match_n, match_p] = get_table_info(team, con_table, 1, 1)
    [penalty_n, penalty_p] = get_table_info(team, penalty_table, 2, 0)
    [opp_pp_n, opp_pp_p] = get_table_info(opp, pp_percent_table, 1, 0)

    last_opponent = stats1[6]

    if stats1[7] in ['1', '2']:
        last_outcome = "vinsten"
    else:
        last_outcome = "förlusten"

    average_conceded = round(con_n / match_n,1)
    average_penalty = round(penalty_n / match_n,1)

    #LINE 0

    if defStrenght < 10:
        line[0] = "En av ligans sämsta försvarsspel. "
    elif defStrenght < 14:
        line[0] = "Mediokert försvarsspel, håller i dagsläget inte för mer än undre halvan av tabellen. "
    elif defStrenght < 17:
        line[0] = "Hyfsat försvarsspel men inte ett av ligans bättre. "
    elif defStrenght < 20:
        line[0] = "Ett av ligans starkaste försvarsspel. "
    else:
        line[0] = "Ett av ligans absolut starkaste försvarsspel. "

    #LINE 1

    if con_p == 14:
        line[1] = team + " har släppt in minst mål i SHL, hittills snittar man " + str(average_conceded) + " mål per match. "
    elif con_p == 13:
        line[1] = team + " har släppt in näst minst mål i SHL, hittills snittar man " + str(average_conceded) + " mål per match. "
    elif con_p == 2:
        line[1] = team + " har släppt in näst mest mål i SHL, hittills snittar man " + str(average_conceded) + " mål per match. "
    elif con_p == 1:
        line[1] = team + " har släppt in mest mål i SHL, hittills snittar man " + str(average_conceded) + " mål per match. "
    else:
        line[1] = team + " har släppt in " + str(average_conceded) + " mål per match under säsongen. "

    #LINE 1

    if con_p > 10:
        if con1 == 0:
            line[2] = "Treden ser fortsatt god ut och man höll nollan senast mot " + last_opponent + ". "
        elif con1 == 1:
            line[2] = "Släppte in 1 mål senast i " + stats1[8] + "-" + stats1[9] + " " + last_outcome + " mot " + last_opponent + ". "
        elif con1 > 4:
            line[2] = "Dock hela " + str(con1) + " mål i baken senast i " + stats1[8] + "-" + stats1[9] + " " + last_outcome + " mot " + last_opponent + ". "
    elif con_p < 5:
        if con1 == 0:
            line[2] = stats1[8] + "-" + stats1[9] + " " + last_outcome + " mot " + last_opponent + " senast var därför en välkommen nolla i den annars ganska dystra statistiken. "
        elif con1 == 1:
            line[2] = "Bättre senast i " + stats1[8] + "-" + stats1[9] + " " + last_outcome + " mot " + last_opponent + ". "
        elif con1 > 4:
            line[2] = "Trenden ser fortsatt mindre bra ut och man släppte in hela " + str(con1) + " mål senast mot " + last_opponent + ". "


    line[2] = "Laget drar på sig " + str(average_penalty) + " utvisningsminuter per match vilket är "

    print(penalty_p)

    penalty_status = 0

    #LINE 2

    if penalty_p == 1:
        line[3] += "mest i ligan. "
        penalty_status = 2
    elif penalty_p in [2,3]:
        line[3] += "bland de högre siffrorna i ligan. "
        penalty_status = 2
    elif penalty_p < 7:
        line[3] += "över snittet i ligan"
        penalty_status = 1
    elif penalty_p > 7 and penalty_p < 13:
        line[3] += "under snittet i ligan. "
        penalty_status = 0
    elif penalty_p == len(penalty_table)-1:
        line[3] += "näst minst i serien. "
        penalty_status = 0
    elif penalty_p == len(penalty_table):
        line[3] += "minst i serien. "
        penalty_status = 0


    #LINE 3

    if penalty_status == "2":
        if opp_pp_p in [1, 2]:
            line[4] = "Detta kan bli ett stort problem då " + opp + " har ett av ligans bästa powerplay. "
        elif opp_pp_p > 0.18 or opp_pp_p in [3, 4]:
            line[4] = "Utvisningar kan bli kostsamt mot " + opp + " som har ett av ligans bästa powerplay. "

    if penalty_status == "1":
        if opp_pp_p in [1, 2, 3, 4] or opp_pp_p > 0.18:
            line[4] = "Utvisningar kan bli avgörande mot " + opp + " som har ett av ligans bästa powerplay. "

    if penalty_status == "0":
        if opp_pp_p in [1, 2, 3, 4]:
            line[4] = "Detta kan vara en stor fördel mot " + opp + " som har ett av ligans bästa powerplay. "
        elif opp_pp_p > 0.18:
            line[4] = "En fördel då utvisningar kommer bli kostsamt mot Powerplay-starka " + opp + ". "

    print(opp_pp_n, opp_pp_p)


    #LINE4



    print(line[0] + line[1] + line[2] + line[3] + line[4])


