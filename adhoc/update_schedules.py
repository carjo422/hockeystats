import datetime
import urllib.request as urllib

import numpy as np

from calcFunctions import create_game_rating
from calcFunctions import create_teamgames
from functions import get_td_content
from functions import isnumber
from functions import transform_date
from scfiles.get_actions import get_actions
from scfiles.get_lineups import get_lineups
from scfiles.get_refs import get_refs
from scfiles.get_stats import get_stats
from scfiles.get_year_statistics import get_year_statistics
from scfiles.official_roster import get_official_roster
from calcFunctions import calculate_team_strength


#To get feedback on how many games to update
t=0
t_count = 0 # Counts number of update

#Input variables on seasons
seasonID = 9171
seasonYear = 2019
serie = "SHL"
score_update = "New" #New if only fill with new scores

#Vectors to scrape in first step
gameVector = []
venueVector = []
audVector = []
dateVector = []
lineVector = []

#Read in season schedule
scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)
response = urllib.urlopen(scheduleUrl)
page_source = str(response.read())

#Establish connection to database
import sqlite3
conn = sqlite3.connect('/Users/carljonsson/Python/hockeystats/hockeystats.db')
c = conn.cursor()

#Check if vectors exist
c.execute("SELECT * FROM schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
sc = c.fetchall()

if len(sc) > 0:
    c.execute("DELETE FROM SCHEDULE where SEASONID = ? and SERIE = ?", [seasonYear, serie])

#If vectors dont exist then get vectors


page_source = page_source.replace("\\xc3\\xa5", "å")
page_source = page_source.replace("\\xc3\\xa4", "ä")
page_source = page_source.replace("\\xc2\\xa0", " ")
page_source = page_source.replace("\\xc3\\xa9", "é")
page_source = page_source.replace("\\xc3\\xb6", "ö")
page_source = page_source.replace("\\xc3\\x84", "Ä")
page_source = page_source.replace("\\xc3\\x85", "Å")
page_source = page_source.replace("\\xc3\\x96", "Ö")
page_source = page_source.replace("\\r", " ")
page_source = page_source.replace("\\n", " ")

for i in range(1,len(page_source)-10):

    if isnumber(page_source[i:i + 4]) and page_source[i + 4] == '-' and isnumber(page_source[i + 5:i + 7]) and page_source[i + 7] and isnumber(page_source[i + 8:i + 10]):
        currdate = page_source[i:i + 10]

    if page_source[i:i+8] == "/Events/":

        gameID = 0

        for j in range(1,10):



            if isnumber(page_source[i+8+j]) == False:
                if gameID == 0:
                    gameID = page_source[i+8:i+8+j]
                    gameVector.append(gameID)
                    dateVector.append(currdate)

        audience = ""

        tds = get_td_content(page_source[i:max(len(page_source)-10,i+200)])

        inserted = 0

        for j in range(0,10):
            if isnumber(tds[j]) and inserted == 0:
                inserted = 1
                audVector.append(int(tds[j]))
                venueVector.append(tds[j+1])

for j in range(0, len(gameVector)):
    c.execute("INSERT INTO schedule (SEASONID, SERIE, GAMEID, GAMEDATE, AUD, VENUE) VALUES (?,?,?,?,?,?)",[seasonYear,serie,gameVector[j],dateVector[j], audVector[j], venueVector[j]])


c.execute("SELECT GAMEID from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
gameVector = c.fetchall()
c.execute("SELECT GAMEDATE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
dateVector = c.fetchall()
c.execute("SELECT AUD from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
audVector = c.fetchall()
c.execute("SELECT VENUE from schedule where SEASONID = ? and SERIE = ?", [seasonYear, serie])
venueVector = c.fetchall()

conn.commit()