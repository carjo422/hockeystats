import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from calcFunctions import create_game_rating

#Update score for games

def re_score(seasonYear,serie):

    c.execute("DELETE FROM teamscore where SEASONID = ? AND SERIE = ?", [seasonYear, serie])
    conn.commit()

    c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
    gameVector = c.fetchall()

    t=0

    if len(gameVector) > 0:

        n=len(gameVector)

        for j in range(0, n):

            # Add score to lineups

            c.execute("SELECT TEAM, NUMBER, FORNAME, SURNAME, GAMEDATE FROM lineups where GAMEID = ?", [gameVector[j][0]])
            lineups = c.fetchall()

            for i in range(0, len(lineups)):

                c.execute("SELECT * from lineups where GAMEID = ? and TEAM = ? and NUMBER = ?",[gameVector[j][0], lineups[i][0], lineups[i][1]])
                lineup = c.fetchall()

                score = create_game_rating(lineup, lineups[i][0], c,conn)

                if len(score) < 4:
                    score = ['0', '0', '0', '0']

                c.execute(
                    "UPDATE lineups SET SCORE = ?, FINALSCORE = ?, OFFSCORE = ?, DEFSCORE = ? WHERE GAMEID = ? and TEAM = ? and NUMBER = ?",
                    [score[0], score[1], score[2], score[3], gameVector[j][0], lineups[i][0], lineups[i][1]])

            t+=1
            print(str(seasonYear) + " " + str(t) + "/" + str(n) + " scores updated")

            conn.commit

        c.close

re_score(2016,'SHL')
#re_score(2017,'SHL')
#re_score(2018,'SHL')
#re_score(2019,'SHL')
