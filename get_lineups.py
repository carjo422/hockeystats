import urllib.request as urllib
from functions import find_str

def get_lineups(id, team1, team2):
    gameUrl = "http://stats.swehockey.se/Game/LineUps/" + str(id)
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())

    output = []
    line = ""
    team = team1

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
        elif page_source[j:j + 8] == "4th Line":
            line = "4th Line"

            if team == team1:
                team = team2
            else:
                team = team1

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

            s3 = find_str(name_string, ".")
            s4 = find_str(name_string, ",")
            s5 = find_str(name_string, "\\")

            surname = name_string[s3 + 1:s4]

            if s5 > 0:
                forname = name_string[s4 + 1:s5]
            else:
                forname = name_string[s4 + 1:]

            output.append([id, team, number, forname, surname, line, startPlayer])

    return output