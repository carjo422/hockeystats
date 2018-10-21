import os.path
print(os.path.abspath(__file__))

import sqlite3
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()


def delete(gameid):

    c.execute("DELETE FROM TEAMGAMES WHERE GAMEID = ?", [gameid])
    c.execute("DELETE FROM TEAMSCORE WHERE GAMEID = ?", [gameid])
    c.execute("DELETE FROM events WHERE GAMEID = ?", [gameid])
    c.execute("DELETE FROM lineups WHERE GAMEID = ?", [gameid])
    c.execute("DELETE FROM refs WHERE GAMEID = ?", [gameid])
    c.execute("DELETE FROM schedule WHERE GAMEID = ?", [gameid])
    c.execute("DELETE FROM stats WHERE GAMEID = ?", [gameid])

    conn.commit()

#delete(393366)

c.execute("SELECT GAMEID FROM stats WHERE SEASONID = ? AND SERIE = ?",[2019, 'HA'])
list = c.fetchall()

for i in range(0,len(list)):
    delete(list[i][0])