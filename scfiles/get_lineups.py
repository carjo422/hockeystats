import urllib.request as urllib
from functions import find_str

def get_lineups(id, audience, venue, season, team1, team2):
    gameUrl = "http://stats.swehockey.se/Game/LineUps/" + str(id)
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())

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

    output = []
    line = ""
    team = team1
    chng1 = 0
    chng2 = 0

    for j in range(1, len(page_source) - 10):

        number = 0
        forname = ""
        surname = ""
        startPlayer = 0


        if page_source[j:j+4] == team1[1:4]:
            team = team1
        elif page_source[j:j+4] == team2[1:4]:
            team = team2

        if page_source[j:j + 8] == "1st Line":
            line = "1st Line"
        elif page_source[j:j + 8] == "2nd Line":
            line = "2nd Line"
        elif page_source[j:j + 8] == "3rd Line":
            line = "3rd Line"

            chng1 += 1
            if chng1 == 2: team = team2

        elif page_source[j:j + 8] == "4th Line":
            line = "4th Line"

            chng2 +=1
            if chng2 == 2: team = team2

        elif page_source[j:j+5] == "Extra":
            line = "Extra players"

        elif page_source[j:j + 7] == "Goalies":
            line = "Goalies"

        if page_source[j:j + 12] == "lineUpPlayer":

            k = 1
            startPlayer = 0

            while page_source[j + 12 + k] != "<":
                name_string = page_source[j + 12:j + 13 + k]
                k += 1

            if "red""" in name_string:
                startPlayer = 1

            s1 = find_str(name_string, ">")
            s2 = find_str(name_string[s1 + 1:-1], ".")

            number = name_string[s1 + 1:s1 + 1 + s2]

            name_string = name_string.replace("\\r\\n", "")
            name_string = name_string.replace(" ", "")
            name_string = name_string.replace("\\xc3\\xb6", "ö")
            name_string = name_string.replace("\\xc3\\xa9", "é")
            name_string = name_string.replace("\\xc3\\xa4", "ä")
            name_string = name_string.replace("\\xc3\\x96", "Ö")

            s3 = find_str(name_string, ".")
            s4 = find_str(name_string, ",")
            s5 = find_str(name_string, "\\")

            surname = name_string[s3 + 1:s4]

            if s5 > 0:
                forname = name_string[s4 + 1:s5]
            else:
                forname = name_string[s4 + 1:]

            if forname.find("(")>0:
                forname = forname[0:forname.find("(")]

            output.append([id, team, number, forname, surname, line, startPlayer, audience, venue, season])

    return output