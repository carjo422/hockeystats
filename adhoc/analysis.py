import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

from create_pre_match_analysis import create_pre_match_analysis

c.execute( "SELECT GAMEDATE, SERIE, HOMETEAM, AWAYTEAM, GAMEID FROM stats WHERE (SEASONID = ? OR SEASONID = ? OR SEASONID = ? OR SEASONID = ?) AND SERIE = ? ORDER BY GAMEID",[2017, 2017, 2017, 2017, 'SHL'])
games = c.fetchall()

print(games)

count = 0

for i in range(0, len(games)):
    count += 1

    gamedate = games[i][0]
    serie = games[i][1]
    hometeam = games[i][2]
    awayteam = games[i][3]
    gameid = games[i][4]

    create_pre_match_analysis(gamedate, serie, hometeam, awayteam, gameid, c, conn)

    print(count, "/", len(games))

if 2 == 3:

    from pandas import ExcelWriter
    import matplotlib.pyplot as plt
    from calcFunctions import calculate_team_strength
    from create_player_tables import create_goal_scorer_characteristics

    #print("Örebro HK",calculate_team_strength("Örebro HK",'2018-10-29',c))
    #print("Frölunda HC",calculate_team_strength("Frölunda HC",'2018-10-29',c))
    #print("Brynäs IF",calculate_team_strength("Brynäs IF",'2018-10-29',c))
    #print("HV 71",calculate_team_strength("HV 71",'2018-10-29',c))
    #print("Linköping HC",calculate_team_strength("Linköping HC",'2018-10-29',c))
    #print("Djurgårdens IF",calculate_team_strength("Djurgårdens IF",'2018-10-29',c))
    #print("Växjö Lakers HC",calculate_team_strength("Växjö Lakers HC",'2018-10-29',c))
    #print("Färjestad BK",calculate_team_strength("Färjestad BK",'2018-10-29',c))
    #print("Skellefteå AIK",calculate_team_strength("Skellefteå AIK",'2018-10-29',c))
    #print("Rögle BK",calculate_team_strength("Rögle BK",'2018-10-29',c))
    #print("Mora IK",calculate_team_strength("Mora IK",'2018-10-29',c))

    #c.execute("SELECT SEASONID, TEAM, FORNAME, SURNAME, GOALS, POSITION FROM ROSTERS WHERE POSITION = ? OR POSITION = ? ORDER BY GOALS",['LD','RD'])
    #print(pd.DataFrame(c.fetchall()))

    #c.execute("SELECT SUM(GOALS), SUM(PPGOALS) FROM lineups WHERE FORNAME = 'Kodie' AND SURNAME = 'Curran'")
    #print(c.fetchall())

    #create_goal_scorer_characteristics(c,conn)

    #c.execute("SELECT * FROM EXP_GOAL_SCORER WHERE POSITION = ? OR POSITION = ?",['LD','RD'])
    #upd = c.fetchall()
    #print(upd)

    #for i in range(0,len(upd)):
    #    gameid = upd[i][3]
    #    forname = upd[i][5]
    #    surname = upd[i][6]
    #    personnr = upd[i][7]
    #
    #    new_pp = upd[i][11]/3.5
    #
    #    c.execute("UPDATE EXP_GOAL_SCORER SET IN_PP = ? WHERE GAMEID = ? AND FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",[new_pp, gameid, forname, surname, personnr])
    #
    #conn.commit()


    #c.execute("SELECT FORNAME, SURNAME, PERSONNR, SUM(CASE WHEN EVENT = ? THEN 1 ELSE 0 END) AS N_GOALS FROM EVENTS WHERE GAMEID IN (SELECT GAMEID FROM STATS WHERE SERIE = ?) GROUP BY FORNAME, SURNAME, PERSONNR ORDER BY N_GOALS DESC",["Goal","SHL"])

    #players = c.fetchall()

    #for i in range(0,20):
    #    c.execute("SELECT GAMEID, TIME FROM EVENTS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND EVENT = ?",[players[i][0], players[i][1], players[i][2], "Goal"])
    #    player_goals = c.fetchall()
    #
    #    total_d = 0
    #    total_w = 0
    #
    #    for j in range(0,len(player_goals)):
    #        c.execute("SELECT a.GAMEID, a.TIME, a.PERSONNR, a.FORNAME, a.SURNAME, b.POSITION, b.LENGHT, b.WEIGHT FROM EVENTS a LEFT JOIN ROSTERS b ON a.PERSONNR = b.PERSONNR AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME WHERE a.SEASONID = b.SEASONID AND a.GAMEID = ? AND a.TIME = ? AND a.EVENT = ? AND (b.POSITION = ? OR b.POSITION = ?)",[player_goals[j][0],player_goals[j][1],"-1","LD","RD"])
    #        player_info = c.fetchall()
    #
    #        for k in range(0,len(player_info)):
    #            total_d += 1
    #            total_w += player_info[k][7]
    #
    #    print(players[i][0], players[i][1], players[i][3], total_d, total_w / total_d)

    c.execute("SELECT * FROM EXP_GOAL_SCORER")
    anl = pd.DataFrame(c.fetchall(), columns=['Serie','Season','Team','Gameid','Gamedate','Forname','Surname','Personnr','Age','Position','Last_Line','Handle','Pos_Score','Pos_Score_Last','Pos_Multiplier','Hist_Scoring', 'Score_Ratio', 'Hist_Scoring_REG', 'Hist_Scoring_PP', 'In_PP','Trend','Weight','Act_Goal','Exp_Goal'])

    #print(anl.to_string)

    data1 = anl[['Pos_Score','Act_Goal']]
    #print("Pos Score Correlation",data1.corr())

    data2 = anl[['Pos_Score_Last','Act_Goal']]
    #print("Pos Score Last Correlation",data2.corr())

    #data3 = anl[['Hist_Scoring','Act_Goal']]



    anl['Pos_Score_Final'] = anl['Pos_Score']*anl['Pos_Multiplier']
    anl['Pos_Score_Final_Last'] = anl['Pos_Score_Last']*anl['Pos_Multiplier']
    anl['Hist_Scoring_REG_Ratio'] = anl['Score_Ratio'] * anl['Hist_Scoring_REG']



    data3 = anl[['Final_Scoring','Position','Act_Goal']]

    #print("Hist Scoreing Correlation",data3.corr())

    #data4 = anl[['In_PP','Act_Goal']]
    #print("In PP Correlation",data4.corr())

    from model_evaluation_scoring import evaluate_scoring_model
    #from model_evaluation_scoring import evaluate_on_groups

    evaluate_scoring_model(data3, ['CE','RW','LW','LD','RD'])

    #anl['Pos_Score_Final_Round'] = round(anl['Pos_Score_Final']/5,2)*5
    #anl['Hist_Scoring_Round'] = round(anl['Hist_Scoring']/5,2)*5

    #evaluate_on_groups(anl[['Position','Final_Scoring','Act_Goal']],'Position')
    #evaluate_on_groups(anl[['Handle','Final_Scoring','Act_Goal']],'Handle')
    #evaluate_on_groups(anl[['Last_Line','Final_Scoring','Act_Goal']],'Last_Line')
    #evaluate_on_groups(anl[['Pos_Score_Final_Round','Final_Scoring','Act_Goal']],'Pos_Score_Final_Round')
    #evaluate_on_groups(anl[['Hist_Scoring_Round','Final_Scoring','Act_Goal']],'Hist_Scoring_Round')
