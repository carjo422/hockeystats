import urllib.request as urllib
from functions import find_str
from functions import get_td_content

def get_refs(id):
    gameUrl = "http://stats.swehockey.se/Game/LineUps/" + str(id)
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())

    get_td_content(page_source)