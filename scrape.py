from functions import isnumber
from functions import find_str
from functions import get_isolated_number
from functions import get_isolated_percent
from functions import get_period_stats
from get_lineups import get_lineups
from get_stats import get_stats
from get_actions import get_actions
from get_refs import get_refs
import urllib.request as urllib
import numpy as np

seasonID = 9006
scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Schedule/" + str(seasonID)

nGames = 0
gameVector = []
lineVector = []


response = urllib.urlopen(scheduleUrl)
page_source = str(response.read())

line = ""

for i in range(1,len(page_source)-10):

    if page_source[i:i+8] == "/Events/":

        gameID = 0

        for j in range(1,10):
            if isnumber(page_source[i+8+j]) == False:
                if gameID == 0:
                    gameID = page_source[i+8:i+8+j]
                    nGames += 1
                    gameVector.append(gameID)


#Download Lineup data from each game

for i in range(0,1):
    #http://stats.swehockey.se/Game/Events/347351/
    #http://stats.swehockey.se/Game/LineUps/347351

    # Download Action data from each game
    stats = get_stats(gameVector[i])
    #lineups = get_lineups(gameVector[i], stats[2], stats[3])
    #actions = get_actions(gameVector[i], stats[2], stats[3])
    get_refs(gameVector[i])



