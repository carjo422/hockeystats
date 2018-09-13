import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import pandas as pd

#c.execute("""CREATE TABLE roster (
#                ID integer,
#                SEASONID integer,
#                TEAM TEXT,
#                NUMBER integer,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                POSITION TEXT)""")

#c.execute("""CREATE TABLE lineups (
#                ID integer,
#                GAMEID integer,
#                SEASONID integer,
#                VENUE TEXT,
#                AUDIENCE integer,
#                HOMETEAM TEXT,
#                AWAYTEAM TEXT,
#                TEAM TEXT,
#                GAMEDATE TEXT,
#                NUMBER integer,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                POSITION TEXT,
#                START_PLAYER integer)""")

#c.execute("""CREATE TABLE events (
#                ID integer,
#                GAMEID integer,
#                SEASONID integer,
#                VENUE TEXT,
#                AUDIENCE integer,
#                PERIOD integer,
#                TIME TEXT,
#                EVENT TEXT,
#                TEAM TEXT,
#                NUMBER TEXT,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                EXTRA1 TEXT,
#                EXTRA2 TEXT)""")

#c.execute("""CREATE TABLE stats (
#                GAMEID integer,
#                GAMEDATE TEXT,
#                SEASONID integer,
#                VENUE TEXT,
#                AUDIENCE integer,
#                HOMETEAM TEXT,
#                AWAYTEAM TEXT,
#                HOMESCORE integer,
#                AWAYSCORE integer,
#                HOMESHOTS integer,
#                AWAYSHOTS integer,
#                HOMESAVES integer,
#                AWAYSAVES integer,
#                HOMEPENALTY integer,
#                AWAYPENALTY integer,
#                HSHOTS1 integer,
#                HSHOTS2 integer,
#                HSHOTS3 integer,
#                HSHOTS4 integer,
#                ASHOTS1 integer,
#                ASHOTS2 integer,
#                ASHOTS3 integer,
#                ASHOTS4 integer,
#                HSAVES1 integer,
#                HSAVES2 integer,
#                HSAVES3 integer,
#                HSAVES4 integer,
#                ASAVES1 integer,
#                ASAVES2 integer,
#                ASAVES3 integer,
#                ASAVES4 integer,
#                HPENALTY1 integer,
#                HPENALTY2 integer,
#                HPENALTY3 integer,
#                HPENALTY4 integer,
#                APENALTY1 integer,
#                APENALTY2 integer,
#                APENALTY3 integer,
#                APENALTY4 integer)""")

#c.execute("""CREATE TABLE refs (
#                GAMEID integer,
#                SEASONID integer,
#                VENUE TEXT,
#                AUDIENCE integer,
#                HOMETEAM TEXT,
#                AWAYTEAM TEXT,
#                REF1 TEXT,
#                REF2 TEXT,
#                LINE1 TEXT,
#                LINE2 TEXT)""")

c.execute(
    "SELECT TEAM, COUNT(ID) as GOALS FROM events where EVENT = ? group by TEAM",
    ["Goal"])

result = c.fetchall()

c.execute(
    "SELECT NUMBER, FORNAME, SURNAME, COUNT(ID) as GOALS FROM events where EVENT = ? or EVENT = ? group by FORNAME, SURNAME, NUMBER order by GOALS DESC",
    ["Goal", "Assist"])

result = c.fetchall()

c.execute(
    "SELECT HOMETEAM, CASE WHEN HSCORE1+HSCORE2+HSCORE3 > ASCORE1+ASCORE2+ASCORE3 THEN ? WHEN HSCORE1+HSCORE2+HSCORE3 = ASCORE1+ASCORE2+ASCORE3 THEN ? ELSE ? END AS RESULT, 1 FROM stats",["ETT","KRYSS","TVÅ"])

result_table = c.fetchall()

result_pandas = pd.DataFrame(result_table, columns = ['Lag', 'Tecken', 'Antal'])
result = result_pandas.pivot_table(index='Lag', columns='Tecken', values='Antal', aggfunc='sum')
[result['PERCENT1'],result['PERCENT2'],result['PERCENT3']] = [round(result['ETT']/26,2),round(result['KRYSS']/26,2),round(result['TVÅ']/26,2)]

result = result.sort_values(['ETT', 'KRYSS'], ascending=[0, 0])

print(result)

c.execute(
    "SELECT AWAYTEAM, CASE WHEN HSCORE1+HSCORE2+HSCORE3 < ASCORE1+ASCORE2+ASCORE3 THEN ? WHEN HSCORE1+HSCORE2+HSCORE3 = ASCORE1+ASCORE2+ASCORE3 THEN ? ELSE ? END AS RESULT, 1 FROM stats",["ETT","KRYSS","TVÅ"])

result_table = c.fetchall()

result_pandas = pd.DataFrame(result_table, columns = ['Lag', 'Tecken', 'Antal'])
result = result_pandas.pivot_table(index='Lag', columns='Tecken', values='Antal', aggfunc='sum')
[result['PERCENT1'],result['PERCENT2'],result['PERCENT3']] = [round(result['ETT']/26,2),round(result['KRYSS']/26,2),round(result['TVÅ']/26,2)]

result = result.sort_values(['ETT', 'KRYSS'], ascending=[0, 0])

print(result)

#result_pandas = result_pandas[result_pandas['Tecken'] == 'ETT']
#test = (result_pandas.groupby(['Lag','Tecken']).sum())
#test['Procent'] = test['Antal']/25

#result = test.sort_values('Antal',ascending=0)

#print(result)