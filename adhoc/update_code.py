#Establish connection to database

import os

if os.path.exists('/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/'):
    data_directory = '/Users/carljonsson/PycharmProjects/GetHockeyData/hockeystats/'
else:
    data_directory = '/Users/carljonsson/Python/hockeystats/'

import sqlite3
conn = sqlite3.connect(data_directory + '/hockeystats.db')
c = conn.cursor()

from calcFunctions import create_game_rating
from calcFunctions import calculate_team_strength

#Update score for games

def re_score(seasonYear,serie):

    c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    gameVector = c.fetchall()

    t=0

    if len(gameVector) > 0:

        n=len(gameVector)

        for j in range(0, len(gameVector)):

            c.execute("DELETE FROM teamscore where gameid = ?", [gameVector[j][0]])
            conn.commit()

            c.execute("SELECT TEAM, GAMEDATE FROM TEAMGAMES WHERE GAMEID = ?", [gameVector[j][0]])
            tgt = c.fetchall()


            [final_team_score, points, season_points, player_score_final] = calculate_team_strength(tgt[0][0],tgt[0][1],c)

            c.execute("SELECT * FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?",[gameVector[j][0],tgt[0][0]])
            ts = c.fetchall()

            if len(ts)>0:
                c.execute("UPDATE TEAMSCORE SET SCORE, FORM_SCORE = ?, LAST_SEASONS_SCORE = ?, PLAYER_SCORE = ? WHERE GAMEID = ? AND TEAM = ?",[final_team_score, points, season_points, player_score_final, gameVector[j][0],tgt[0][0]])
            else:
                c.execute("INSERT INTO TEAMSCORE (SEASONID, SERIE, GAMEID, GAMEDATE, TEAM, SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE) VALUES (?,?,?,?,?,?,?,?,?)",[seasonYear, serie, gameVector[j][0], tgt[0][1], tgt[0][0], final_team_score, points, season_points, player_score_final])


            [final_team_score, points, season_points, player_score_final] = calculate_team_strength(tgt[1][0],tgt[1][1], c)

            c.execute("SELECT * FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?", [gameVector[j][0], tgt[1][0]])
            ts = c.fetchall()

            if len(ts) > 0:
                c.execute(
                    "UPDATE TEAMSCORE SET SCORE, FORM_SCORE = ?, LAST_SEASONS_SCORE = ?, PLAYER_SCORE = ? WHERE GAMEID = ? AND TEAM = ?",
                    [final_team_score, points, season_points, player_score_final, gameVector[j][0], tgt[1][0]])
            else:
                c.execute(
                    "INSERT INTO TEAMSCORE (SEASONID, SERIE, GAMEID, GAMEDATE, TEAM, SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE) VALUES (?,?,?,?,?,?,?,?,?)",
                    [seasonYear, serie, gameVector[j][0], tgt[1][1], tgt[1][0], final_team_score, points, season_points,
                     player_score_final])

            conn.commit()


            [final_team_score, points, season_points, player_score_final] = calculate_team_strength(tgt[1][0],tgt[1][1], c)


            # Add score to lineups

            c.execute("SELECT TEAM, NUMBER, FORNAME, SURNAME, GAMEDATE FROM lineups where GAMEID = ?", [gameVector[j][0]])
            lineups = c.fetchall()

            for i in range(0, len(lineups)):

                c.execute("SELECT * from lineups where GAMEID = ? and TEAM = ? and NUMBER = ?",[gameVector[j][0], lineups[i][0], lineups[i][1]])
                lineup = c.fetchall()

                score = create_game_rating(lineup, lineups[i][0], c,conn)
                #print(score)

                if len(score) < 4:
                    score = ['0', '0', '0', '0']

                c.execute(
                    "UPDATE lineups SET SCORE = ?, FINALSCORE = ?, OFFSCORE = ?, DEFSCORE = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",
                    [score[0], score[1], score[2], score[3], gameVector[j][0], lineups[i][0], lineups[i][1]])

            t+=1
            print(str(seasonYear) + " " + str(t) + "/" + str(n) + " scores updated")

            conn.commit

        c.close

def goals_to_model_table():

    c.execute("SELECT GAMEID, HSCORE1+HSCORE2+HSCORE3, ASCORE1+ASCORE2+ASCORE3 FROM stats")
    upd = c.fetchall()

    for i in range(0,len(upd)):
        c.execute("UPDATE EXP_SHOTS_TABLE SET ACT_GOALS1 = ?, ACT_GOALS2 = ? WHERE GAMEID = ?",[upd[i][1],upd[i][2],upd[i][0]])

    conn.commit()


c.execute("SELECT HOMETEAM, AWAYTEAM, GAMEDATE FROM EXP_SHOTS_TABLE")
upd = c.fetchall()

count=0

for i in range(0,len(upd)):
    [a, b, d, hts] = calculate_team_strength(upd[i][0], upd[i][2], c)
    [a, b, d, ats] = calculate_team_strength(upd[i][1], upd[i][2], c)

    c.execute("UPDATE EXP_SHOTS_TABLE SET SCORE1 = ?, SCORE2 = ? WHERE HOMETEAM = ? AND AWAYTEAM = ? AND GAMEDATE = ?",[hts, ats, upd[i][0], upd[i][1], upd[i][2]])
    count+=1

    print(count)

conn.commit()

#re_score(2016,'SHL')
#re_score(2016,'HA')
#re_score(2017,'SHL')
#re_score(2017,'HA')
#re_score(2018,'SHL')
#re_score(2018,'HA')
#re_score(2019,'SHL')
#re_score(2019,'HA')

#goals_to_model_table()