import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import numpy as np
import pandas as pd
from pandas import ExcelWriter
import matplotlib.pyplot as plt
from calcFunctions import calculate_team_strength

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

c.execute("SELECT GAMEID, GAMEDATE FROM GOALS_FOREST_TABLE_2")
tst = c.fetchall()

for i in range(0,len(tst)):

    seasonYear = int(tst[i][1][0:4])
    if int(tst[i][1][5:7]) > 6:
        seasonYear += 1

    c.execute("UPDATE GOALS_FOREST_TABLE_2 SET SEASONID = ? WHERE GAMEID = ?",[seasonYear, tst[i][0]])

conn.commit()




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

if 1 == 5:

    tst = pd.DataFrame(c.fetchall())
    writer = ExcelWriter('efficiency.xlsx')
    tst.to_excel(writer,'Sheet1')
    writer.save()
