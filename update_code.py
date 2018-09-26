import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from calcFunctions import create_game_rating

c.execute("SELECT * FROM lineups")
full_lineup = c.fetchall()

n = len(full_lineup)
print(n)

c.execute("SELECT * FROM lineups where id = ?",[45555])
lineup = c.fetchall()

score = create_game_rating(lineup, c, lineup[0][8])

#print(score)