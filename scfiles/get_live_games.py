import datetime
import urllib.request as urllib

import numpy as np

from functions import get_td_content
from functions import isnumber
from functions import transform_date
from scfiles.get_stats import get_stats

#Vectors to scrape in first step
def get_live_games(seasonID, gamedate, home_team, away_team):

    gameid = ""

    gameVector = []

    #Read in season schedule
    scheduleUrl = "http://stats.swehockey.se/ScheduleAndResults/Live/" + str(seasonID)
    response = urllib.urlopen(scheduleUrl)
    page_source = str(response.read())

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

            stats = get_stats(gameID, gamedate)

            if home_team == stats[2] and away_team == stats[3]:
                gameid = gameID

    return gameid
