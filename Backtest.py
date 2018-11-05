import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()



import pandas as pd
from pandas import ExcelWriter
import numpy as np
import scipy

backtest = 1
backtest_keeper = 0
from create_pre_match_analysis import create_pre_match_analysis

if backtest == 1:

    c.execute("SELECT GAMEDATE, SERIE, TEAM, OPPONENT, GAMEID FROM TEAMGAMES WHERE (SEASONID = ? OR SEASONID = ? OR SEASONID = ? OR SEASONID = ?) AND SERIE = ? AND HOMEAWAY = ? ORDER BY GAMEDATE ",[2019, 2019, 2019, 2019, 'SHL', 'H'])
    lst = c.fetchall()

    #Create DataFrames

    exp_results = pd.DataFrame(np.zeros((11, 11)))
    act_results = pd.DataFrame(np.zeros((11, 11)))

    exp_1X2 = pd.DataFrame(np.zeros((1, 3)), columns = ['1','X','2'])
    act_1X2 = pd.DataFrame(np.zeros((1, 3)), columns = ['1','X','2'])

    exp_45 = pd.DataFrame(np.zeros((1, 2)), columns=['O45', 'U45'])
    act_45 = pd.DataFrame(np.zeros((1, 2)), columns=['O45', 'U45'])

    exp_goals_home = 0
    act_goals_home = 0
    exp_goals_away = 0
    act_goals_away = 0

    nGames = 0
    predict = 0

    scorePredict = pd.DataFrame(np.zeros((0, 14)))
    scorePredict.columns = ['GameID','Team','Predicted keeper','Actual keeper','nGames','L%','R%','D%','F%','Total goals','L Goals','R Goals','D Goals','F Goals']

    for i in range(0,len(lst)):


        results, odds1X2, odds45, exp_hg, exp_ag, hg, ag, ks_home, ks_away  = create_pre_match_analysis(lst[i][0],lst[i][1],lst[i][2],lst[i][3],lst[i][4],c,conn)

        nGames += 1

        # Code to compare outcomes Actual vs expected

        exp_1X2['1'] += odds1X2['1']
        exp_1X2['X'] += odds1X2['X']
        exp_1X2['2'] += odds1X2['2']

        exp_45['O45'] += odds45['O45']
        exp_45['U45'] += odds45['U45']

        if hg > ag:
            act_1X2['1'] += 1
            predict+=odds1X2['1']
        if hg == ag:
            act_1X2['X'] += 1
            predict += odds1X2['X']
        if hg < ag:
            act_1X2['2'] += 1
            predict += odds1X2['2']

        if hg+ag > 4:
            act_45['O45'] += 1
        if hg + ag <= 4:
            act_45['U45'] += 1

        exp_goals_home += exp_hg
        act_goals_home += exp_ag
        exp_goals_away += hg
        act_goals_away += ag

        if backtest_keeper == 1:

            # Create goal scorer vs keeper DataFrame

            # Home team

            ks_home = ks_home.sort_values(['Start%','nCon'], ascending=[0,0])

            ks_home_predicted = ks_home.iloc[0]

            # Which keeper is predicted to start

            pred_keeper1 = [ks_home_predicted['Forname'],ks_home_predicted['Surname']]

            # Get actual keeper data

            c.execute("SELECT FORNAME, SURNAME FROM LINEUPS WHERE GAMEID = ? AND TEAM = ? AND POSITION = ? AND START_PLAYER = 1",[lst[i][4], lst[i][2], "Goalies"])
            act_keep = c.fetchall()[0]

            act_keeper1 = [act_keep[0],act_keep[1]]

            pL = ks_home_predicted['L%']
            pR = ks_home_predicted['R%']
            pD = ks_home_predicted['D%']
            pF = ks_home_predicted['F%']

            # What was the real outcome of the game

            c.execute("SELECT a.FORNAME, a.SURNAME, a.PERSONNR, b.HANDLE, b.POSITION FROM EVENTS a LEFT JOIN ROSTERS b ON a.FORNAME = b.FORNAME AND a.SURNAME = b.SURNAME AND a.PERSONNR = b.PERSONNR AND a.SEASONID = b.SEASONID WHERE a.GAMEID = ? AND a.EVENT = ? AND a.TEAM != ?",[lst[i][4], "Goal", lst[i][2]])
            goal_data = c.fetchall()

            act_goals = 0

            aL = 0
            aR = 0
            aD = 0
            aF = 0

            for k in range(0, len(goal_data)):
                if goal_data[k][4] in ['LW', 'RW', 'CE']:
                    if goal_data[k][3] == 'L':
                        aL += 1
                        act_goals += 1
                    elif goal_data[k][3] == 'R':
                        aR += 1
                        act_goals += 1
                    if goal_data[k][4] in ['LD','RD']:
                        aD += 1
                    elif goal_data[k][4] in ['LW','RW','CE']:
                        aF += 1

            scorePredict = scorePredict.append({'GameID' : lst[i][4], 'Team' : lst[i][2], 'Predicted keeper' : pred_keeper1, 'Actual keeper' : act_keeper1, 'nGames' : ks_home_predicted['nCon'], 'L%' : pL, 'R%' : pR,'D%' : pD, 'F%' : pF, 'Total goals' : act_goals, 'L Goals' : aL, 'R Goals' : aR, 'D Goals' : aD, 'F Goals' : aF}, ignore_index=True)

            # Away team

            ks_away = ks_away.sort_values(['Start%', 'nCon'], ascending=[0, 0])

            ks_away_predicted = ks_away.iloc[0]

            # Which keeper is predicted to start

            pred_keeper2 = [ks_away_predicted['Forname'], ks_away_predicted['Surname']]

            # Get actual keeper data

            c.execute("SELECT FORNAME, SURNAME FROM LINEUPS WHERE GAMEID = ? AND TEAM = ? AND POSITION = ? AND START_PLAYER = 1",[lst[i][4], lst[i][3], "Goalies"])
            act_keep = c.fetchall()[0]

            act_keeper2 = [act_keep[0], act_keep[1]]

            pL = ks_away_predicted['L%']
            pR = ks_away_predicted['R%']
            pD = ks_away_predicted['D%']
            pF = ks_away_predicted['F%']

            # What was the real outcome of the game

            c.execute("SELECT a.FORNAME, a.SURNAME, a.PERSONNR, b.HANDLE, b.POSITION FROM EVENTS a LEFT JOIN ROSTERS b ON a.FORNAME = b.FORNAME AND a.SURNAME = b.SURNAME AND a.PERSONNR = b.PERSONNR AND a.SEASONID = b.SEASONID WHERE a.GAMEID = ? AND a.EVENT = ? AND a.TEAM != ?",[lst[i][4], "Goal", lst[i][3]])
            goal_data = c.fetchall()

            act_goals = 0

            aL = 0
            aR = 0
            aD = 0
            aF = 0

            for k in range(0, len(goal_data)):
                if goal_data[k][4] in ['LW', 'RW', 'CE']:
                    if goal_data[k][3] == 'L':
                        aL += 1
                        act_goals += 1
                    elif goal_data[k][3] == 'R':
                        aR += 1
                        act_goals += 1
                    if goal_data[k][4] in ['LD', 'RD']:
                        aD += 1
                    elif goal_data[k][4] in ['LW', 'RW', 'CE']:
                        aF += 1

            scorePredict = scorePredict.append({'GameID': lst[i][4], 'Team': lst[i][3], 'Predicted keeper': pred_keeper2, 'Actual keeper': act_keeper2, 'nGames' : ks_away_predicted['nCon'], 'L%': pL, 'R%': pR, 'D%': pD, 'F%': pF, 'Total goals': act_goals, 'L Goals': aL, 'R Goals': aR,'D Goals': aD, 'F Goals': aF}, ignore_index=True)

            print(lst[i][4], "loaded")

    predictability = predict / nGames

    print(exp_1X2)
    print(act_1X2)

    print(exp_45)
    print(act_45)

    print(exp_goals_home)
    print(act_goals_home)
    print(exp_goals_away)
    print(act_goals_away)

    print("Prediction:", predictability)

    writer = ExcelWriter('Pre_match_analysis.xlsx')
    #scorePredict.to_excel(writer, 'Keeper_matrix')
    writer.save()