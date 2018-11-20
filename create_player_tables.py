import pandas as pd
import numpy as np
import openpyxl
from pandas import ExcelWriter


def get_player_data(team, gameid, gamedate, odds, seasonYear, serie, c, conn):

    #Get all players in current team

    c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND gamedate < ?",[team, seasonYear, gamedate])
    players1 = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr'])

    #If first game
    if len(players1) == 0:
        c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND gamedate = ?",[team, seasonYear, gamedate])
        players1 = pd.DataFrame(c.fetchall(), columns=['Forname', 'Surname', 'Personnr'])

    c.execute("SELECT FORNAME, SURNAME, PERSONNR FROM ROSTERS WHERE TEAM = ? AND SEASONID = ?",[team, seasonYear])
    players2 = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr'])

    for i in range(0,len(players1)):

        add_player = 1

        for j in range(0,len(players2)):

            if players1['Forname'][i] == players2['Forname'][j] and players1['Surname'][i] == players2['Surname'][j]:

                add_player = 0

            if players1['Personnr'][i] == players2['Personnr'][j] and players1['Personnr'][i] != "":

                if players1['Forname'][i] == players2['Forname'][j] and players1['Surname'][i][0:2] == players2['Surname'][j][0:2]:
                    add_player = 0

                if players1['Surname'][i] == players2['Surname'][j] and players1['Forname'][i][0:3] == players2['Forname'][j][0:3]:
                    add_player = 0

        if add_player == 1:

            players2 = players2.append({'Forname': players1['Forname'][i], 'Surname': players1['Surname'][i], 'Personnr': players1['Personnr'][i]},ignore_index=True)


    #print(players2)

    current_season = pd.DataFrame(columns=['Forname', 'Surname', 'Personnr', 'LastYear', 'Position', 'Handle', 'Length', 'Weight', 'Games', 'Goals', 'Assist', 'Plus', 'Minus', 'InPP', 'InBP', 'Line1%', 'Line2%','Line3%', 'Line4%', 'Extra%'])

    for i in range(0,len(players2)):

        forname = players2['Forname'][i]
        surname = players2['Surname'][i]
        personnr = players2['Personnr'][i]

        c.execute("SELECT POSITION, HANDLE, LENGHT, WEIGHT FROM ROSTERS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? ORDER BY SEASONID DESC",[forname, surname, personnr])
        rst = c.fetchall()

        position = ""
        handle = ""
        weight = ""
        length = ""

        if len(rst) > 0:
            position = rst[0][0]
            handle = rst[0][1]
            weight = rst[0][2]
            length = rst[0][3]

        c.execute("""SELECT GAMEDATE,
                            DATEDIFF(month, GAMEDATE, PERSONNR)
                            GOALS,
                            ASSISTS,
                            PLUS,
                            MINUS,
                            CAST(INPOWERPLAY AS FLOAT))/COUNT(GAMEID),
                            CAST(INBOXPLAY AS FLOAT))/COUNT(GAMEID),
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END
                        FROM
                            LINEUPS
                        WHERE
                            FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND GAMEDATE < ?
                        GROUP BY
                            FORNAME, SURNAME, PERSONNR""", ['1st Line', '2nd Line', '3rd Line', '4th Line', 'Extra players', forname, surname, personnr, seasonYear, gamedate])

        sts = c.fetchall()

        print(sts)



    #######################################################################################################
    ######                         Calculate total goal score % for the players                       #####
    #######################################################################################################

    goal_scorer = pd.DataFrame(columns=['Forname','Surname','Position','Pos Score','Hist Score','PP Score','Goal%','Odds'])


    ############################################################################################################################################################################
    ######                                                         Create the base scoring value for the player                                                            #####
    ############################################################################################################################################################################

    ##Percentage goals lines - 1st (33.5%), 2nd (30%), 3rd (23%), 4th (13%)
    ##Percentage goals poisitions - CE (27.25%), RW (27.25%), LW (29.5%), D (8%)

    if odds < 0.2:
        odds = 0.2
    if odds > 0.65:
        odds = 0.65

    if position_new == 'CE':
        base_scoring = 0.20+odds*0.225
    elif position_new == 'RW':
        base_scoring = 0.2725-odds*0.1125
    elif position_new == 'LW':
        base_scoring = 0.295-odds*0.1125
    elif position_new in ["LD","RD"]:
        base_scoring = 0.08
    else:
        base_scoring = 0

    #Line scoring
    line_scoring = games_new * (line1_new*0.335+line2_new*0.30+line3_new*0.23+line4_new*0.13)
    line_scoring /= (games_new)

    base_scoring *= line_scoring

    #Plus minus ratio

    c.execute("SELECT SUM(HSCORE1+HSCORE2+HSCORE3+HSCORE4+ASCORE1+ASCORE2+ASCORE3+ASCORE4)/SUM(1) FROM STATS WHERE SEASONID = ?",[seasonYear-1])
    agl = c.fetchall()
    if len(agl) == 0:
        average_goal = 5
    else:
        average_goal = agl[0][0]

    if games_new > 0:
        pm = (plus_new + minus_new) / games_new / average_goal
    else:
        pm = 0.265

    pm_games = min(games_new,5)
    pm_ratio = (1 - games_new * 0.08) * base_scoring + pm * games_new*0.08

    ############################################################################################################################################################################
    ######                                                        Create the in PP scoring value for the player                                                            #####
    ############################################################################################################################################################################

    inPP = inPP_new * games_new + inPP_old * games_old / 4
    inPP /= (games_new + games_old / 4)

    if position_new in ['LD','RD']:
        inPP /= 3.5

    inPP /= 2.25

    if inPP > 0.25:
        inPP = 0.25

    ############################################################################################################################################################################
    ######                                                       Create the history scoring value for the player                                                            #####
    ############################################################################################################################################################################

    if games_new + games_old/4 > 0:
        hist_scoring = (goals_new + goals_old/4) / (games_new + games_old/4) / 2.5
    else:
        if position_new == 'GK':
            hist_scoring = 0
        elif position_new in ['LD','RD']:
            hist_scoring = 0.02
        else:
            hist_scoring = 0.08

    if games_new + games_old < 12:
        hist_scoring = hist_scoring * (games_new+games_old)/12 + base_scoring * (12-games_new-games_old)/12

    if hist_scoring > 0.25:
        hist_scoring = 0.25


    #PUT TOGETHER INTO ONE FORMULA BASED ON MODELING

    adjusted_scoring = base_scoring*0.5+hist_scoring*0.4+inPP*0.065 #This is the basic calculation for goals



    c.execute("SELECT * FROM EXP_GOAL_SCORER WHERE GAMEID = ? AND FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",[gameid, forname, surname, personnr])
    chk = c.fetchall()

    if len(chk) > 0:
        pass
    else:

        c.execute("SELECT SUM(1), SUM(CASE WHEN FORNAME = ? AND SURNAME = ? AND PERSONNR = ? THEN 1 ELSE 0 END) FROM EVENTS WHERE EVENT = ? AND TEAM = ? AND GAMEID = ?",[forname,surname,personnr,'Goal', team, gameid])
        gls = c.fetchall()

        if len(gls) > 0 and gls[0][0] != None:

            act_goal = gls[0][1] / gls[0][0]

            c.execute("INSERT INTO EXP_GOAL_SCORER (SERIE, SEASONID, TEAM, GAMEID, GAMEDATE, FORNAME, SURNAME, PERSONNR, POSITION, BASE_SCORING, HIST_SCORING, IN_PP, ACT_GOAL) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",[serie, seasonYear, team, gameid, gamedate, forname, surname, personnr, position_new, base_scoring, hist_scoring, inPP, act_goal])

    goal_scorer = goal_scorer.append({'Forname': current_season['Forname'][i], 'Surname': current_season['Surname'][i], 'Position': position_new, 'Pos Score': base_scoring, 'Hist Score': hist_scoring, 'PP Score': inPP, 'Goal%': round(adjusted_scoring,3), 'Odds': round(1/adjusted_scoring,1)}, ignore_index = True)

    goal_scorer = goal_scorer.sort_values('Odds',ascending=True)
    #odds = round(adjusted_scoring,3),round(1/adjusted_scoring,1)

    conn.commit()

    print(goal_scorer.to_string())
    print(goal_scorer['Goal%'].sum())

    return current_season



def get_keeper_data(team, gamedate, seasonYear, c, conn):

    #Collect all players in the team

    c.execute("SELECT a.FORNAME, a.SURNAME, a.PERSONNR, b.POSITION, b.HANDLE, a.TEAM, SUM(1), SUM(a.GOALS), SUM(a.PPGOALS), SUM(a.ASSISTS), SUM(a.PLUS) FROM (SELECT * FROM LINEUPS WHERE GAMEID IN (SELECT GAMEID FROM TEAMGAMES WHERE TEAM = ? AND GAMEDATE < ? AND SEASONID = ?)) a LEFT JOIN ROSTERS b on a.FORNAME = b.forname AND a.SURNAME = b.SURNAME and a.TEAM = b.TEAM WHERE a.TEAM = ? AND b.SEASONID = ? GROUP BY a.FORNAME, a.SURNAME",[team, gamedate, seasonYear,team, seasonYear])
    output = c.fetchall()
    teamplayers = pd.DataFrame(output)

    #print(teamplayers)

    if len(output) == 0:

        c.execute("SELECT FORNAME, SURNAME, PERSONNR, POSITION, HANDLE, TEAM, 0, 0, 0, 0, 0 FROM ROSTERS WHERE SEASONID = ? AND TEAM = ?",[seasonYear,team])
        output = c.fetchall()
        teamplayers = pd.DataFrame(output)

        #print(teamplayers)


    #Check rosters for all scorers


    keeper_stat = pd.DataFrame(np.zeros((0, 8)), columns=['Forname', 'Surname', 'nCon', 'L%', 'R%', 'D%', 'F%', 'Start%'])


    for i in range(0,len(output)):

        if teamplayers[3][i] != 'GK':

            c.execute("SELECT SEASONID, FORNAME, SURNAME, PERSONNR, TEAM, GAMES, GOALS, CAST(GOALS AS FLOAT)/GAMES ASSIST, PLUS, SEASONID-SUBSTR(PERSONNR,1,4) FROM ROSTERS WHERE SUBSTR(FORNAME,1,3) = ? AND SUBSTR(SURNAME,1,2) = ? AND PERSONNR = ? AND SEASONID < ? ORDER BY SEASONID ASC",[teamplayers[0][i][0:3],teamplayers[1][i][0:2],teamplayers[2][i], seasonYear])
            scorer_hist = c.fetchall()

            weight = 0
            scoring = 0

            if len(scorer_hist) > 0:
                for j in range(0,len(scorer_hist)):

                    if scorer_hist[j][5] != None:

                        season_weight = float(scorer_hist[j][5]) / (float(seasonYear)-float(scorer_hist[j][0])+1)

                        weight += season_weight

                        age_adjustment = 1
                        if scorer_hist[j][9] > 30:
                            age_adjustment = 0.97

                        scoring += scorer_hist[j][7]*season_weight*age_adjustment

            if weight > 0:
                scoring /= weight

            #print("W",weight)
            #print("S",scoring)

        else:

            c.execute("SELECT DISTINCT a.GAMEID FROM events a LEFT JOIN STATS b on a.gameid = b.gameid where SUBSTR(a.FORNAME,1,3) = ? AND SUBSTR(a.SURNAME,1,2) = ? AND a.PERSONNR = ? AND a.PERSONNR != ? AND b.GAMEDATE < ?",[teamplayers[0][i][0:3],teamplayers[1][i][0:2],teamplayers[2][i],"", gamedate])
            game_list = c.fetchall()

            n_conceded = 0
            concL = 0
            concR = 0
            concD = 0
            concF = 0

            startp = 0

            if len(game_list) > 0:
                for j in range(0,len(game_list)):

                    c.execute("SELECT GAMEID, TIME, TEAM, FORNAME, SURNAME, PERSONNR, EVENT, SEASONID FROM EVENTS WHERE GAMEID = ? AND (EVENT = ? OR EVENT = ? OR EVENT = ?) ORDER BY TIME",[game_list[j][0],"GK In","GK Out","Goal"])
                    events = c.fetchall()

                    goalie_in = 0

                    for k in range(0,len(events)):
                        if events[k][3][0:3] == teamplayers[0][i][0:3] and events[k][4][0:2] == teamplayers[1][i][0:2] and events[k][5] == teamplayers[2][i] and events[k][6] == "GK In":
                            g_team = events[k][2]
                            goalie_in = 1

                        if events[k][3][0:3] == teamplayers[0][i][0:3] and events[k][4][0:2] == teamplayers[1][i][0:2] and events[k][5] == teamplayers[2][i] and events[k][6] == "GK Out":
                            goalie_in = 0

                        if goalie_in == 1 and events[k][6] == "Goal" and g_team != events[k][2]:
                            #print(events[k])
                            n_conceded += 1

                            c.execute("SELECT HANDLE, POSITION FROM ROSTERS WHERE SUBSTR(FORNAME,1,3) = ? AND SUBSTR(SURNAME,1,2) = ? AND PERSONNR = ? AND SEASONID = ?",[events[k][3][0:3],events[k][4][0:2],events[k][5],events[k][7]])
                            LR = c.fetchall()


                            if len(LR) > 0:

                                if LR[0][0] == "R":
                                    concR += 1
                                elif LR[0][0] == "L":
                                    concL += 1

                                if LR[0][1] in ['LD','RD']:
                                    concD += 1
                                elif LR[0][1] in ['LW','RW','CE']:
                                    concF += 1


            c.execute("SELECT COUNT(GAMEID) FROM TEAMGAMES WHERE TEAM = ? AND SEASONID = ? AND GAMEDATE < ?",[teamplayers[5][i], seasonYear, gamedate])
            n_games = c.fetchall()[0][0]+0.5
            c.execute("SELECT COUNT(GAMEID) FROM LINEUPS WHERE SUBSTR(FORNAME,1,3) = ? AND SUBSTR(SURNAME,1,2) = ? AND PERSONNR = ? AND TEAM = ? AND START_PLAYER = ? AND SEASONID = ? AND GAMEDATE < ?",[teamplayers[0][i][0:3],teamplayers[1][i][0:2],teamplayers[2][i],teamplayers[5][i],1,seasonYear, gamedate])
            n_games_keeper = c.fetchall()[0][0]+0.5

            pL = 0
            pR = 0
            pD = 0
            pF = 0

            if concL > 0:
                pL = concL/(concR+concL)
            if concR > 0:
                pR = concR / (concR + concL)
            if concR > 0:
                pD = concD / (concD + concF)
            if concR > 0:
                pF = concF / (concD + concF)

            keeper_stat = keeper_stat.append({'Forname' : teamplayers[0][i], 'Surname' : teamplayers[1][i], 'nCon' : n_conceded, 'L%' : pL, 'R%' : pR, 'D%' : pD, 'F%' : pF, 'Start%' : n_games_keeper}, ignore_index = True)

    keeper_sum = keeper_stat['Start%'].sum()
    keeper_stat['Start%'] = keeper_stat['Start%'] / keeper_sum

    return keeper_stat


def create_goal_scorer_characteristics(c,conn):

    c.execute("SELECT CASE WHEN EXTRA1 = ? THEN 'PP' ELSE 'NM' END AS EXTRA, COUNT(ID) FROM events WHERE EVENT = ? GROUP BY EXTRA",['PP','Goal'])
    anl1 = pd.DataFrame(c.fetchall(), columns = ["Extra","Goals"])
    anl1["Goals%"] = anl1["Goals"]/anl1["Goals"].sum()
    print(anl1)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN lineups b ON a.GAMEID = b.GAMEID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR WHERE EVENT = ? AND b.POSITION in (?,?,?,?,?) GROUP BY b.POSITION",['Goal','1st Line','2nd Line','3rd Line','4th Line','Extra players'])
    anl2 = pd.DataFrame(c.fetchall(), columns = ["Line","Goals"])
    anl2["Goals%"] = anl2["Goals"]/anl2["Goals"].sum()
    print(anl2)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN ROSTERS b ON a.SEASONID = b.SEASONID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR WHERE EVENT = ? AND b.POSITION in (?,?,?,?,?) GROUP BY b.POSITION",['Goal','CE','LD','LW','RD','RW'])
    anl3 = pd.DataFrame(c.fetchall(), columns=["Position", "Goals"])
    anl3["Goals%"] = anl3["Goals"] / anl3["Goals"].sum()
    print(anl3)

    #c.execute("SELECT FORNAME, SURNAME, TEAM, GAMES, GOALS FROM ROSTERS WHERE GOALS >= 0 AND TEAM = ? AND SEASONID = ?",['HV 71',2018])
    #anl5 = pd.DataFrame(c.fetchall(), columns = ['Förnamn','Efternamn','Lag','Matcher','Mål'])
    #anl5['Mål total'] = anl5["Mål"].sum()
    #anl5['Mål%'] = anl5['Mål']*52/anl5['Matcher']/anl5['Mål total']
    #anl5 = anl5.sort_values(['Mål%'], ascending = [0])
    #print(anl5)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN ROSTERS b ON a.SEASONID = b.SEASONID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR LEFT JOIN EXP_SHOTS_TABLE c ON a.gameid = c.gameid WHERE a.EVENT = ? AND a.TEAM = c.AWAYTEAM AND b.POSITION in (?,?,?,?,?) AND c.ODDS2 < 0.25 GROUP BY b.POSITION",['Goal', 'CE', 'LD', 'LW', 'RD', 'RW'])
    anl5 = pd.DataFrame(c.fetchall(), columns=["Position", "Goals"])
    anl5["Goals%"] = anl5["Goals"] / anl5["Goals"].sum()
    print(anl5)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN ROSTERS b ON a.SEASONID = b.SEASONID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR WHERE EVENT = ? AND b.POSITION in (?,?,?,?,?) AND EXTRA1 = ? GROUP BY b.POSITION",['Goal', 'CE', 'LD', 'LW', 'RD', 'RW','PP'])
    anl6 = pd.DataFrame(c.fetchall(), columns=["Position", "Goals"])
    anl6["Goals%"] = anl6["Goals"] / anl6["Goals"].sum()
    print(anl6)


    #Basic distrubution is set
    #Adjustment based on specific line strength

    #Adjust for keeper weakness vs D/F and L/R
    #Adjust for player strenght vs defenders
    #Stats vs keeper
    #Stats vs defenders

    #Does different players score for favourites/underdogs (LOTS OF FUCKING CENTER GOALS IN FAVOURITES, WINGS IN UNDERDOGS) (ANL5)
    #Is form important? // NO IT DOESNT MATTER IF THE PLAYER SCORED LAST GAME
    #Adjustment based on specific player strength (ready in code)

    #First/last analysis

    #First and last goals? Something important?

    #Is form important?
    #
    #c.execute("SELECT FORNAME, SURNAME, TEAM FROM ROSTERS WHERE SEASONID = 2018 AND GOALS > 10")
    #players = c.fetchall()
    #
    #n0 = 0
    #g0 = 0
    #n1 = 0
    #g1 = 0
    #
    #for i in range(0,len(players)):
    #
    #    forname = players[i][0]
    #    surname = players[i][1]
    #    team = players[i][2]
    #
    #    c.execute("SELECT GAMEID, GAMEDATE, GOALS FROM LINEUPS WHERE SEASONID = ? AND TEAM = ? AND FORNAME = ? AND SURNAME = ? ORDER BY GAMEDATE",[2018, team, forname, surname])
    #    tSerie = (pd.DataFrame(c.fetchall()))
    #
    #
    #
    #    for i in range(1,len(tSerie)):
    #        if tSerie[2][i-1] == 0:
    #            n0+=1
    #            if tSerie[2][i] > 0:
    #                g0+=1
    #        else:
    #            n1 += 1
    #            if tSerie[2][i] > 0:
    #                g1 += 1


    #print(n0,g0,n1,g1)






