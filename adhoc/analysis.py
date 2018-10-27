import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import numpy as np
import pandas as pd
from pandas import ExcelWriter
import matplotlib.pyplot as plt


c.execute("SELECT FORNAME, SURNAME, PERSONNR, SUM(CASE WHEN EVENT = ? THEN 1 ELSE 0 END) AS N_GOALS FROM EVENTS WHERE GAMEID IN (SELECT GAMEID FROM STATS WHERE SERIE = ?) GROUP BY FORNAME, SURNAME, PERSONNR ORDER BY N_GOALS DESC",["Goal","SHL"])

players = c.fetchall()

for i in range(0,20):
    c.execute("SELECT GAMEID, TIME FROM EVENTS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND EVENT = ?",[players[i][0], players[i][1], players[i][2], "Goal"])
    player_goals = c.fetchall()

    total_d = 0
    total_w = 0

    for j in range(0,len(player_goals)):
        c.execute("SELECT a.GAMEID, a.TIME, a.PERSONNR, a.FORNAME, a.SURNAME, b.POSITION, b.LENGHT, b.WEIGHT FROM EVENTS a LEFT JOIN ROSTERS b ON a.PERSONNR = b.PERSONNR AND a.FORNAME = b.FORNAME and a.SURNAME = b.SURNAME WHERE a.SEASONID = b.SEASONID AND a.GAMEID = ? AND a.TIME = ? AND a.EVENT = ? AND (b.POSITION = ? OR b.POSITION = ?)",[player_goals[j][0],player_goals[j][1],"-1","LD","RD"])
        player_info = c.fetchall()

        for k in range(0,len(player_info)):
            total_d += 1
            total_w += player_info[k][7]

    print(players[i][0], players[i][1], players[i][3], total_d, total_w / total_d)

if 1 == 5:

    tst = pd.DataFrame(c.fetchall())
    writer = ExcelWriter('efficiency.xlsx')
    tst.to_excel(writer,'Sheet1')
    writer.save()
