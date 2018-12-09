import pandas as pd
import numpy as np
import openpyxl
from pandas import ExcelWriter
from functions import linreg


def get_player_position(forname, surname, gamedate, team, seasonYear, c, conn):
    c.execute("SELECT GAMEID, POSITION FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND TEAM = ? AND GAMEDATE < ?",[forname, surname, team, gamedate])
    player = c.fetchall()

    position = "LD"
    handle = "L"

    if len(player) > 0:

        RW = 0
        LW = 0
        CE = 0
        LD = 0
        RD = 0
        GK = 0

        for i in range(0,len(player)):
            gameid = player[0][0]
            line = player[0][1]

            c.execute("SELECT b.POSITION FROM LINEUPS a LEFT JOIN ROSTERS b ON a.forname = b.forname AND a.surname = b.surname AND a.team = b.team WHERE GAMEID = ? AND a.TEAM = ? AND a.POSITION = ? AND b.SEASONID = ?",[gameid, team, line, seasonYear])
            pos = c.fetchall()

            nD = 0
            nO = 0

            nCE = 0
            nLW = 0
            nRW = 0
            nLD = 0
            nRD = 0
            nGK = 0

            nGolie = 0

            if len(pos) > 0:
                for j in range(0,len(pos)):
                    if pos[j][0] == 'CE':
                        nO += 1
                        nCE += 1
                    if pos[j][0] == 'RW':
                        nO += 1
                        nRW += 1
                    if pos[j][0] == 'LW':
                        nO += 1
                        nLW += 1
                    if pos[j][0] == 'LD':
                        nD += 1
                        nLD += 1
                    if pos[j][0] == 'RD':
                        nD += 1
                        nRD += 1
                    if pos[j][0] == 'GK':
                        nGK += 1

            if nO == 3:
                if nLD == 1:
                    RD+=1
                else:
                    LD+=1

            if nO < 3:
                if nGK > 0:
                    GK+=1
                elif nCE == 0:
                    CE+=1
                elif nRW == 0:
                    RW+=1
                else:
                    LW+=1

    if max(GK,LD,RD,LW,RW,CE) == GK:
        position = "GK"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == LD:
        position = "LD"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == RD:
        position = "RD"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == LW:
        position = "LW"
        handle = "L"
    elif max(GK, LD, RD, LW, RW, CE) == RW:
        position = "RW"
        handle = "R"
    elif max(GK, LD, RD, LW, RW, CE) == CE:
        position = "CE"
        handle = "L"

    return position,handle

def get_player_data(team, gameid, gamedate, odds, seasonYear, serie, c, conn):

    #Get all players in current team

    goal_scorer = pd.DataFrame(columns = ['Serie','Season','Team','Gameid','Gamedate','Forname','Surname','Personnr','Age','Position','Last Line', 'Act Line','Handle','Pos Score','Pos Score Last','Pos multiplier','Score ratio','Hist Score','Last Ten Score','Hist Score Reg','Hist Score PP','PP Score','Trend%','Weight'])

    c.execute("SELECT GAMEID FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ? AND GAMEDATE < ? ORDER BY GAMEDATE DESC LIMIT 1 ",[seasonYear, team, gamedate])
    lst = c.fetchall()

    last_id = ''

    if len(lst) > 0:
        last_id = lst[0][0]

    c.execute("SELECT  FORNAME, SURNAME, PERSONNR, POSITION FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND GAMEID = ? AND POSITION != ?",[team, seasonYear, last_id, 'Goalies'])
    players = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr','Line'])

    #If first game
    if len(players) == 0:
        c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR, POSITION FROM LINEUPS WHERE TEAM = ? AND SEASONID = ? AND GAMEDATE = ? AND POSITION != ?",[team, seasonYear, gamedate,'Goalies'])
        players = pd.DataFrame(c.fetchall(), columns=['Forname', 'Surname', 'Personnr','Line'])


    tot1 = 0
    tot2 = 0

    for i in range(0,len(players)):

        #############################################################################################################################
        #####                                              BASIC DATA + LINE                                                    #####
        #############################################################################################################################

        forname = players['Forname'][i]
        surname = players['Surname'][i]
        personnr = players['Personnr'][i]
        line = players['Line'][i]

        act_line = line

        c.execute("SELECT POSITION FROM LINEUPS WHERE GAMEDATE = ? AND FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",[gamedate, forname, surname, personnr])
        act = c.fetchall()
        if len(act) > 0:
            act_line = act[0][0]
        else:
            act_line = "Out"

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
                            SEASONID,
                            SERIE,
                            GAMEDATE-PERSONNR,
                            GOALS,
                            ASSISTS,
                            PLUS,
                            MINUS,
                            CAST(INPOWERPLAY AS FLOAT),
                            CAST(INBOXPLAY AS FLOAT),
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END,
                            CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END
                        FROM
                            LINEUPS
                        WHERE
                            (FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND TEAM = ? AND GAMEDATE < ?
                        OR
                            FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND TEAM = ? AND GAMEDATE < ?)
                        GROUP BY
                            FORNAME, SURNAME, PERSONNR, GAMEID
                        ORDER BY
                            GAMEDATE DESC""", ['1st Line', '2nd Line', '3rd Line', '4th Line', 'Extra players', forname, surname, personnr, team, gamedate, forname, surname, '', team, gamedate])

        sts = c.fetchall()

        #print(sts)

        #CURRENT SEASON LINE SCORE

        n_games_old = 0
        oldLine = [0,0,0,0,0]
        plus_minus = 0

        if len(sts) > 0:
            for j in range(0, len(sts)):
                if sts[j][1] <= seasonYear:
                    n_games_old += 1/(seasonYear*5-sts[j][1]*5+1)

                    oldLine[0] += sts[j][10]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[1] += sts[j][11]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[2] += sts[j][12]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[3] += sts[j][13]/(seasonYear*5-sts[j][1]*5+1)
                    oldLine[4] += sts[j][14]/(seasonYear*5-sts[j][1]*5+1)

                    plus_minus += (sts[j][6]*1.25+sts[j][7]*0.5)/(seasonYear*5-sts[j][1]*5+1) * 0.2


        # NUMBER OF GAMES LINE SCORE

        line_score_old = 0

        if n_games_old > 0:
            for j in range(0,len(oldLine)):
                oldLine[j] /= n_games_old

            plus_minus /= n_games_old

        line_score_old += oldLine[0] * 0.3175
        line_score_old += oldLine[1] * 0.2950
        line_score_old += oldLine[2] * 0.2350
        line_score_old += oldLine[3] * 0.1450
        line_score_old += oldLine[4] * 0.0075

        if personnr != '':
            age = int(gamedate[0:4])-int(personnr[0:4])
        else:
            if n_games_old > 0:
                age = 18
            else:
                age = 30

        #FIND POSITION IF NOT AVAILABLE IN ROSTER

        if position == '':
            if line_score_old > 0.02 and plus_minus > 0.02:

                position, handle = get_player_position(forname, surname, gamedate, team, seasonYear, c, conn)

        # ADJUST GK - THEY DONT SCORE

        if position == "GK":
            line_score_old = 0
            plus_minus = 0

        tot1 += line_score_old
        tot2 += plus_minus

        #ADJUST PLAYERS WITHOUT GAME HISTORY

        if n_games_old == 0:
            if age <= 18:
                line_score_old = 0.025
                plus_minus = 0.025
            elif age <= 21:
                line_score_old = 0.06
                plus_minus = 0.06
            elif age <= 24:
                line_score_old = 0.1
                plus_minus = 0.1
            else:
                line_score_old = 0.18
                plus_minus = 0.18

        #NO ADJUSTMENT ON AGE AT THIS STAGE

        base_scoring = round(line_score_old / 2 + plus_minus / 2, 3)

        #############################################################################################################################
        #####                                               HISTORIC SCORING                                                    #####
        #############################################################################################################################

        from functions import transform_date

        if personnr == '':
            c.execute("SELECT SEASONID, SERIE, COUNT(GAMEID), SUM(GOALS), SUM(ASSISTS), SUM(PLUS), SUM(PPGOALS) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND TEAM = ? AND GAMEDATE < ? GROUP BY SEASONID ORDER by SEASONID",[forname, surname, team, gamedate])
            hist = c.fetchall()
            c.execute("SELECT SEASONID, SERIE, COUNT(GAMEID), SUM(GOALS), SUM(ASSISTS), SUM(PLUS), SUM(PPGOALS) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND TEAM = ? AND GAMEDATE < ? AND GAMEDATE > ? GROUP BY SEASONID ORDER by SEASONID",[forname, surname, team, gamedate, transform_date(gamedate,40)])
            short_hist = c.fetchall()
        else:
            c.execute("SELECT SEASONID, SERIE, COUNT(GAMEID), SUM(GOALS), SUM(ASSISTS), SUM(PLUS), SUM(PPGOALS) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND GAMEDATE < ? GROUP BY SEASONID ORDER by SEASONID",[forname, surname, personnr, gamedate])
            hist = c.fetchall()
            c.execute("SELECT SEASONID, SERIE, COUNT(GAMEID), SUM(GOALS), SUM(ASSISTS), SUM(PLUS), SUM(PPGOALS) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND GAMEDATE < ? AND GAMEDATE > ? GROUP BY SEASONID ORDER by SEASONID",[forname, surname, personnr, gamedate, transform_date(gamedate,40)])
            short_hist = c.fetchall()

        if len(hist) > 0:

            score_trend = pd.DataFrame(columns=['Year','nGames','goalsTeam','goalsPlayer','assistPlayer','plusPlayer','goalPercent','regGoalPercent','PPGoalPercent','Weight'])

            for j in range(0,len(hist)):

                if personnr == '':
                    c.execute("SELECT COUNT(a.gameid), SUM(b.SCORE1) FROM LINEUPS a LEFT JOIN TEAMGAMES b ON a.gameid = b.gameid WHERE b.TEAM = a.TEAM AND a.SEASONID = ? AND forname = ? AND surname = ? AND a.team = ?",[hist[j][0], forname, surname, team])
                    goals = c.fetchall()
                else:
                    c.execute("SELECT COUNT(a.gameid), SUM(b.SCORE1) FROM LINEUPS a LEFT JOIN TEAMGAMES b ON a.gameid = b.gameid WHERE b.TEAM = a.TEAM AND a.SEASONID = ? AND forname = ? AND surname = ? AND personnr = ?",[hist[j][0], forname, surname, personnr])
                    goals = c.fetchall()

                if len(goals) > 0:
                    total_goals = goals[0][1]
                else:
                    total_goals = 0

                if total_goals == 0:
                    goal_percent = 0
                else:
                    goalPercent = hist[j][3] / total_goals
                    regGoalPercent = (hist[j][3]-hist[j][6]) * 4/3 / total_goals #4/3 since 75% goals non PP
                    PPGoalPercent = hist[j][6]* 4 / total_goals # 4 since 25% goals PP

                score_trend = score_trend.append({
                     'Year': seasonYear-hist[j][0],
                     'nGames': hist[j][2],
                     'goalsTeam': total_goals,
                     'goalsPlayer': hist[j][3],
                     'assistPlayer': hist[j][4],
                     'plusPlayer': hist[j][5],
                     'goalPercent': goalPercent,
                    'regGoalPercent': regGoalPercent,
                    'PPGoalPercent': PPGoalPercent,
                    'Weight': hist[j][2]/(seasonYear-hist[j][0]+1)
                }, ignore_index=True)


            #Calculate average scoring of player

            average_score_percent = 0
            average_assist_percent = 0
            average_plus_percent = 0
            average_score_percent_regular = 0
            average_score_percent_PP = 0

            total_weight = 0

            score_trend['s_weight'] = score_trend['goalPercent'] * score_trend['Weight']
            average_score_percent += score_trend['s_weight'].sum() / score_trend['Weight'].sum()

            score_trend['a_weight'] = score_trend['assistPlayer'] / score_trend['goalsTeam'] * score_trend['Weight']
            average_assist_percent += score_trend['a_weight'].sum() / score_trend['Weight'].sum()

            score_trend['p_weight'] = score_trend['plusPlayer'] / score_trend['goalsTeam'] * score_trend['Weight']
            average_plus_percent += score_trend['p_weight'].sum() / score_trend['Weight'].sum()

            score_trend['sr_weight'] = score_trend['regGoalPercent'] * score_trend['Weight']
            average_score_percent_regular += score_trend['sr_weight'].sum() / score_trend['Weight'].sum()

            score_trend['sp_weight'] = score_trend['PPGoalPercent'] * score_trend['Weight']
            average_score_percent_PP += score_trend['sp_weight'].sum() / score_trend['Weight'].sum()

            #Total weight

            total_weight = score_trend['Weight'].sum()

            #Calculate trend of scoring
            a=0
            b=0
            trend = 0

            if len(hist) > 3:

                x = score_trend['goalPercent'].tolist()

                if hist[j][2] < 7:
                    x = (x[0:len(x)-1])

                a, b = linreg(range(len(x)), x)
            else:
                valid_trend = 0

            valid_trend = 1

            for t in range(0,len(hist)):
                if score_trend['Weight'][t] < 2:
                    valid_trend = 0

            if valid_trend == 1:
                trend = a

            if trend == 0:
                if age < 18:
                    trend = 0.01
                elif age < 19:
                    trend = 0.008
                elif age < 20:
                    trend = 0.006
                elif age < 22:
                    trend = 0.003
                elif age > 32:
                    trend = -0.0075

            # Get the base score from last game

            base_score_last= 0

            if line == '1st Line':
                base_score_last = 0.3175
            elif line == '2nd Line':
                base_score_last = 0.2950
            elif line == '3rd Line':
                base_score_last = 0.2350
            elif line == '4th Line':
                base_score_last = 0.1450
            elif line == 'Extra players':
                base_score_last = 0.0075

            # Add goal % based on position in line

            pos_score_percent = 0
            score_ratio = 1

            if position == "CE":
                pos_score_percent = 0.17+odds*0.30
                score_ratio = pos_score_percent / 0.26
            elif position == "LW":
                pos_score_percent = 0.3450-odds*0.15
                score_ratio = pos_score_percent / 0.30
            elif position == "RW":
                pos_score_percent = 0.3250-odds*0.15
                score_ratio = pos_score_percent / 0.28
            elif position in ["LD","RD"]:
                pos_score_percent = 0.08
                score_ratio = 1

            #############################################################################################################################
            #####                                                GET the in PP                                                      #####
            #############################################################################################################################

            total_games = 0
            pp_games = 0

            if personnr == "":
                c.execute("SELECT DISTINCT GAMEID FROM EVENTS WHERE FORNAME = ? AND SURNAME = ? AND TEAM = ?",[forname, surname, team])
                gms = c.fetchall()
                if len(gms) > 0:
                    total_games = len(gms)
            else:
                c.execute("SELECT DISTINCT GAMEID FROM EVENTS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",[forname, surname, personnr])
                gms = c.fetchall()
                if len(gms) > 0:
                    total_games = len(gms)

            if personnr == "":
                c.execute("SELECT DISTINCT GAMEID FROM EVENTS WHERE FORNAME = ? AND SURNAME = ? AND TEAM = ? AND EXTRA1 = ? AND EVENT = ?",[forname, surname, team, 'PP', '1'])
                gms = c.fetchall()
                if len(gms) > 0:
                    pp_games = len(gms)
            else:
                c.execute("SELECT DISTINCT GAMEID FROM EVENTS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND EXTRA1 = ? AND EVENT = ?",[forname, surname, personnr, 'PP', '1'])
                gms = c.fetchall()
                if len(gms) > 0:
                    pp_games = len(gms)

            inPP = 0

            if total_games > 0:
                inPP = pp_games / total_games

            if total_games < 5:
                inPP = inPP * total_games/5 + 0.2 * (5-total_games)/5


            #SHORT TERM SCORING

            short_time_score = average_score_percent
            short_time_score_final = average_score_percent

            if len(short_hist) > 0:
                weight = short_hist[0][2]
                weight_old = (10-min(10,weight))/2

                if position in ['CE','LW','RW']:
                    short_time_score = (short_hist[0][3] * 0.65 + short_hist[0][6]*0.35 * 0.35)/weight/2.4
                elif position in ['LD','RD']:
                    short_time_score = (short_hist[0][3] * 0.65 + short_hist[0][6]*0.35 * 0.35)/weight/2.4

                short_time_score_final = average_score_percent*weight_old/(weight+weight_old)+short_time_score*weight/(weight+weight_old)
                #print(forname, surname, short_hist[0][3], short_time_score_final)


            c.execute("SELECT * FROM EXP_GOAL_SCORER WHERE GAMEID = ? AND FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",[gameid, forname, surname, personnr])
            chk = c.fetchall()

            if len(chk) > 0:
                c.execute("SELECT SUM(1), SUM(CASE WHEN FORNAME = ? AND SURNAME = ? AND PERSONNR = ? THEN 1 ELSE 0 END) FROM EVENTS WHERE EVENT = ? AND TEAM = ? AND GAMEID = ?",[forname, surname, personnr, 'Goal', team, gameid])
                gls = c.fetchall()

                if len(gls) > 0 and gls[0][0] != None:
                    act_goal = gls[0][1] / gls[0][0]
                    # Insert new variables to analysis
                    c.execute("UPDATE EXP_GOAL_SCORER SET SERIE=?, SEASONID=?, TEAM=?, GAMEID=?, GAMEDATE=?, FORNAME=?, SURNAME=?, PERSONNR=?, AGE=?, POSITION=?, LAST_LINE=?, ACT_LINE=?, HANDLE=?, POS_SCORE=?, SCORE_RATIO=?, POS_SCORE_LAST=?, POS_MULTIPLIER=?, HIST_SCORING=?, LAST_TEN_SCORE=?, HIST_SCORING_REG=?, HIST_SCORING_PP=?, IN_PP=?, TREND=?, WEIGHT=?, ACT_GOAL=? WHERE GAMEID = ? AND FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",
                              [serie, seasonYear, team, gameid, gamedate, forname, surname, personnr, age, position, line, act_line, handle, base_scoring, base_score_last, pos_score_percent, score_ratio, average_score_percent,short_time_score_final, average_score_percent_regular, average_score_percent_PP, inPP, trend,total_weight, act_goal, gameid, forname, surname, personnr])

            else:

                c.execute("SELECT SUM(1), SUM(CASE WHEN FORNAME = ? AND SURNAME = ? AND PERSONNR = ? THEN 1 ELSE 0 END) FROM EVENTS WHERE EVENT = ? AND TEAM = ? AND GAMEID = ?",[forname,surname,personnr,'Goal', team, gameid])
                gls = c.fetchall()

                if len(gls) > 0 and gls[0][0] != None:

                    act_goal = gls[0][1] / gls[0][0]
                    #Insert new variables to analysis
                    c.execute("INSERT INTO EXP_GOAL_SCORER (SERIE, SEASONID, TEAM, GAMEID, GAMEDATE, FORNAME, SURNAME, PERSONNR, AGE, POSITION, LAST_LINE, ACT_LINE, HANDLE, POS_SCORE, SCORE_RATIO, POS_SCORE_LAST, POS_MULTIPLIER, HIST_SCORING, LAST_TEN_SCORE, HIST_SCORING_REG, HIST_SCORING_PP, IN_PP, TREND, WEIGHT, ACT_GOAL) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                              [serie, seasonYear, team, gameid, gamedate, forname, surname, personnr, age, position, line, act_line, handle, base_scoring, base_score_last, pos_score_percent, score_ratio, average_score_percent, short_time_score_final, average_score_percent_regular, average_score_percent_PP, inPP, trend, total_weight, act_goal])

            goal_scorer = goal_scorer.append({'Serie': serie, 'Season': seasonYear, 'Team': team, 'Gameid': gameid, 'Gamedate': gamedate, 'Forname': forname, 'Surname': surname, 'Personnr': personnr, 'Age': age, 'Position': position, 'Last Line': line, 'Act Line': act_line, 'Handle': handle, 'Pos Score': base_scoring, 'Pos Score Last': base_score_last, 'Pos multiplier': pos_score_percent, 'Score ratio': score_ratio, 'Hist Score': average_score_percent, 'Last Ten Score': short_time_score_final, 'Last Ten Score': short_time_score,  'Hist Score Reg': average_score_percent_regular, 'Hist Score PP': average_score_percent_PP, 'PP Score': inPP, 'Trend%': trend, 'Weight': total_weight}, ignore_index = True)

    goal_scorer = goal_scorer.sort_values('Hist Score',ascending=False)
    #print(goal_scorer.to_string())

    conn.commit()

    return goal_scorer



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
            n_games = c.fetchall()[0][0]+0.25
            c.execute("SELECT COUNT(GAMEID) FROM LINEUPS WHERE SUBSTR(FORNAME,1,3) = ? AND SUBSTR(SURNAME,1,2) = ? AND PERSONNR = ? AND TEAM = ? AND START_PLAYER = ? AND SEASONID = ? AND GAMEDATE < ?",[teamplayers[0][i][0:3],teamplayers[1][i][0:2],teamplayers[2][i],teamplayers[5][i],1,seasonYear, gamedate])
            n_games_keeper = c.fetchall()[0][0]+0.25

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

    keeper_stat['L'] = keeper_stat['L%']*keeper_stat['nCon']
    keeper_stat['R'] = keeper_stat['R%']*keeper_stat['nCon']
    keeper_stat['D'] = keeper_stat['D%']*keeper_stat['nCon']
    keeper_stat['F'] = keeper_stat['F%']*keeper_stat['nCon']

    n_con_total = keeper_stat['nCon'].sum()


    L_Total = keeper_stat['L'].sum()/n_con_total
    R_Total = keeper_stat['R'].sum()/n_con_total
    D_Total = keeper_stat['D'].sum()/n_con_total
    F_Total = keeper_stat['F'].sum()/n_con_total


    keeper_stat = keeper_stat.append({'Forname' : "GK", 'Surname' : "Total", 'nCon' : n_con_total, 'L%' : L_Total, 'R%' : R_Total, 'D%' : D_Total, 'F%' : F_Total, 'Start%' : 1}, ignore_index = True)

    return keeper_stat


def create_goal_scorer_characteristics(c,conn):

    c.execute("SELECT CASE WHEN EXTRA1 = ? THEN 'PP' ELSE 'NM' END AS EXTRA, COUNT(ID) FROM events WHERE EVENT = ? GROUP BY EXTRA",['PP','Goal'])
    anl1 = pd.DataFrame(c.fetchall(), columns = ["Extra","Goals"])
    anl1["Goals%"] = anl1["Goals"]/anl1["Goals"].sum()
    print(anl1)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN lineups b ON a.GAMEID = b.GAMEID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR WHERE EVENT = ? AND EXTRA1 NOT IN (?) AND b.POSITION in (?,?,?,?,?) GROUP BY b.POSITION",['Goal','PP','1st Line','2nd Line','3rd Line','4th Line','Extra players'])
    anl2 = pd.DataFrame(c.fetchall(), columns = ["Line","Goals"])
    anl2["Goals%"] = anl2["Goals"]/anl2["Goals"].sum()
    print(anl2)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN ROSTERS b ON a.SEASONID = b.SEASONID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR WHERE EVENT = ? AND EXTRA1 NOT IN (?) AND b.POSITION in (?,?,?,?,?) GROUP BY b.POSITION",['Goal','PP','CE','LD','LW','RD','RW'])
    anl3 = pd.DataFrame(c.fetchall(), columns=["Position", "Goals"])
    anl3["Goals%"] = anl3["Goals"] / anl3["Goals"].sum()
    print(anl3)

    #c.execute("SELECT FORNAME, SURNAME, TEAM, GAMES, GOALS FROM ROSTERS WHERE GOALS >= 0 AND TEAM = ? AND SEASONID = ?",['HV 71',2018])
    #anl5 = pd.DataFrame(c.fetchall(), columns = ['Förnamn','Efternamn','Lag','Matcher','Mål'])
    #anl5['Mål total'] = anl5["Mål"].sum()
    #anl5['Mål%'] = anl5['Mål']*52/anl5['Matcher']/anl5['Mål total']
    #anl5 = anl5.sort_values(['Mål%'], ascending = [0])
    #print(anl5)

    c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN ROSTERS b ON a.SEASONID = b.SEASONID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR LEFT JOIN EXP_SHOTS_TABLE c ON a.gameid = c.gameid WHERE a.EVENT = ? AND a.TEAM = c.AWAYTEAM AND EXTRA1 NOT IN (?) AND b.POSITION in (?,?,?,?,?) AND c.ODDS2 > 0.5 GROUP BY b.POSITION",['Goal', 'PP', 'CE', 'LD', 'LW', 'RD', 'RW'])
    anl5 = pd.DataFrame(c.fetchall(), columns=["Position", "Goals"])
    anl5["Goals%"] = anl5["Goals"] / anl5["Goals"].sum()
    print(anl5)

    #c.execute("SELECT b.POSITION, COUNT(a.ID) FROM EVENTS a LEFT JOIN ROSTERS b ON a.SEASONID = b.SEASONID AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME and a.PERSONNR = b.PERSONNR WHERE EVENT = ? AND b.POSITION in (?,?,?,?,?) AND EXTRA1 = ? GROUP BY b.POSITION",['Goal', 'CE', 'LD', 'LW', 'RD', 'RW','PP'])
    #anl6 = pd.DataFrame(c.fetchall(), columns=["Position", "Goals"])
    #anl6["Goals%"] = anl6["Goals"] / anl6["Goals"].sum()
    #print(anl6)


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






