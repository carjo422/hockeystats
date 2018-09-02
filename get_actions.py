import urllib.request as urllib
from functions import find_str

def get_actions(id, team1, team2):
    gameUrl = "http://stats.swehockey.se/Game/Actions/" + str(id)
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())