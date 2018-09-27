import urllib.request as urllib
from functions import find_str
from functions import get_td_content
from functions import isnumber
from functions import get_all_numbers

def get_official_roster(seasonID, season, serie):

    gameUrl = "http://stats.swehockey.se/Teams/Info/TeamRoster/" + str(seasonID) + ""
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())
    output = []

    page_source = page_source.replace("\\xc3\\xa5", "å")
    page_source = page_source.replace("\\xc3\\xa4", "ä")
    page_source = page_source.replace("\\xc2\\xa0", " ")
    page_source = page_source.replace("\\xc3\\xa9", "é")
    page_source = page_source.replace("\\xc3\\xb6", "ö")
    page_source = page_source.replace("\\xc3\\x84", "Ä")
    page_source = page_source.replace("\\xc3\\x85", "Å")
    page_source = page_source.replace("\\xc3\\x96", "Ö")
    page_source = page_source.replace("\\xc3\\xa8", "é")

    page_source = page_source.replace("\\r", " ")
    page_source = page_source.replace("\\n", " ")

    content = get_td_content(page_source)

    for i in range(3,len(content)-3):

        player = []

        if "Team Roster" in content[i]:
            team = content[i - 2]

        if "Youth club" in content[i] or (isnumber(content[i+1]) and "," in content[i+2] and "-" in content[i+3]):
            player.append(season)
            player.append(team)
            player.append(serie)
            player.append(content[i + 1])

            n = content[i + 2].find(",")

            name = content[i + 2][0:n]
            surname = content[i+2][n+1:len(content[i+2])]

            if surname[0] == " ":
                surname = surname[1:len(surname)]

            player.append(name)
            player.append(surname)

            player.append(content[i + 3])
            player.append(content[i + 4])
            player.append(content[i + 5])
            player.append(content[i + 6])
            player.append(content[i + 7])
            player.append(content[i + 8][0:3])

            #print(player)

            output.append(player)

    #print(output)

    return output