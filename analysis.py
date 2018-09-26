import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()
import numpy as np

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


#TEST

from calcFunctions import calculate_team_strength

print(calculate_team_strength("Linköping HC",'2018-09-20'))