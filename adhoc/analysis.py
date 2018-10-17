import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import numpy as np
import pandas as pd
from pandas import ExcelWriter
import matplotlib.pyplot as plt

#Create correlation matrix

if 1 == 5:

    c.execute("SELECT * FROM OUTCOME_PREDICTER")
    tst = c.fetchall()

    dataframe = pd.DataFrame(tst)

    plt.matshow(dataframe.corr())

    print(dataframe.corr())


    # DF TO EXCEL
    from pandas import ExcelWriter

    writer = ExcelWriter('PythonExport.xlsx')
    dataframe.corr().to_excel(writer,'Sheet5')
    writer.save()


    #Shots as a predictor of goals

    c.execute("SELECT (SHOTS11 + SHOTS12 + SHOTS13) as SHOTS, SUM(SCORE11+SCORE12+SCORE13)*100/COUNT(GAMEID) as AVE_GOALS FROM TEAMGAMES WHERE HOMEAWAY = ? GROUP BY SHOTS ORDER BY SHOTS",["H"])
    score_shots = pd.DataFrame(c.fetchall())

    #writer = ExcelWriter('shots_goals_home.xlsx')
    #score_shots.to_excel(writer,'Sheet1')
    #writer.save()

    c.execute("SELECT (SHOTS21 + SHOTS22 + SHOTS23) as SHOTS, SUM(SCORE21+SCORE22+SCORE23)*100/COUNT(GAMEID) as AVE_GOALS FROM TEAMGAMES WHERE HOMEAWAY = ? GROUP BY SHOTS ORDER BY SHOTS",["H"])
    score_shots = pd.DataFrame(c.fetchall())

    writer = ExcelWriter('shots_goals_away.xlsx')
    score_shots.to_excel(writer,'Sheet1')
    writer.save()


#Shots /Goals / Points table

    c.execute("""SELECT TEAM, SUM(4-outcome) as POINTS, SUM(SHOTS11 + SHOTS12 + SHOTS13) as SHOTS1, SUM(SCORE11+SCORE12+SCORE13) as SCORE1, SUM(SHOTS21 + SHOTS22 + SHOTS23) as SHOTS2, SUM(SCORE21+SCORE22+SCORE23) as SCORE2, COUNT(GAMEID) FROM TEAMGAMES WHERE SEASONID = ? AND TEAM = ?
                    AND (OPPONENT = ? OR OPPONENT = ? OR OPPONENT = ?) AND SERIE = ? AND HOMEAWAY = ? GROUP BY TEAM ORDER BY POINTS DESC""",[2018, "Växjö Lakers HC", "Örebro HK", "Rögle BK", "Leksands IF", "SHL", "H"])
    table = pd.DataFrame(c.fetchall())
    print(table)

    writer = ExcelWriter('shots_goals_table_extra.xlsx')
    table.to_excel(writer, 'Sheet1')
    writer.save()

    c.execute("SELECT TEAM, SUM(4-outcome) as POINTS, SUM(SHOTS11 + SHOTS12 + SHOTS13) as SHOTS1, SUM(SCORE11+SCORE12+SCORE13) as SCORE1, SUM(SHOTS21 + SHOTS22 + SHOTS23) as SHOTS2, SUM(SCORE21+SCORE22+SCORE23) as SCORE2, COUNT(GAMEID) as GAMES FROM TEAMGAMES WHERE SEASONID = ? AND SERIE = ? GROUP BY TEAM ORDER BY POINTS DESC",[2019, "SHL"])
    table = pd.DataFrame(c.fetchall())
    print(table)

    writer = ExcelWriter('shots_goals_table_2019.xlsx')
    table.to_excel(writer, 'Sheet1')
    writer.save()

    c.execute("SELECT AWAYTEAM, SUM(EXP_SHOTS2*10)/COUNT(EXP_SHOTS2), SUM(ACT_SHOTS2*10)/COUNT(ACT_SHOTS2) as ACT_SHOTS FROM EXP_SHOTS_TABLE GROUP BY AWAYTEAM ORDER BY ACT_SHOTS DESC")
    tst = c.fetchall()
    print(pd.DataFrame(tst))

c.execute("SELECT ACT_SHOTS1, SUM(EXP_SHOTS1), SUM(ACT_SHOTS1), SUM(EXP_GOAL1), SUM(ACT_GOAL2) FROM EXP_SHOTS_TABLE WHERE SEASON > 2015 GROUP BY ACT_SHOTS1 ORDER BY ACT_SHOTS1")

tst = pd.DataFrame(c.fetchall())
writer = ExcelWriter('efficiency.xlsx')
tst.to_excel(writer,'Sheet1')
writer.save()
