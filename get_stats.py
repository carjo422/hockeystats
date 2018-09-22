from functions import get_isolated_number
from functions import isnumber
from functions import get_isolated_percent
from functions import get_period_stats
import urllib.request as urllib


def get_stats(id, gamedate):
    gameUrl = "http://stats.swehockey.se/Game/LineUps/" + str(id)
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())

    page_source = page_source.replace("\\xc3\\xa5", "å")
    page_source = page_source.replace("\\xc3\\xa4", "ä")
    page_source = page_source.replace("\\xc3\\xa9", "é")
    page_source = page_source.replace("\\xc3\\xb6", "ö")
    page_source = page_source.replace("\\xc3\\x84", "Ä")
    page_source = page_source.replace("\\xc3\\x85", "Å")
    page_source = page_source.replace("\\xc3\\x96", "Ö")

    team_string = ""
    num_vect = []
    pct_vect = []
    period_list = []
    output = []

    for j in range(1, len(page_source) - 10):

        if page_source[j] == ">":
            exNum = get_isolated_number(page_source, j)
            if exNum == 0 or exNum >= 1:
                num_vect.append(exNum)

            exPct = get_isolated_percent(page_source, j)
            if exPct >= 0:
                pct_vect.append(exPct)

        if page_source[j] == "(":
            period_vector = get_period_stats(page_source, j)
            if period_vector != []:
                period_list.append(period_vector)

        if page_source[j:j + 17] == "\\xc2\\xa0-\\xc2\\xa0":

            isf = 0
            s1 = 0
            s2 = 0

            for k in range(1, 35):
                if isf == 0 and j - k > 0:
                    if page_source[j - k] == ">":
                        isf = 1
                        s1 = j - k

            isf = 0

            for k in range(1, 60):
                if isf == 0 and j + k < len(page_source):
                    if page_source[j + k] == "<":
                        isf = 1
                        s2 = j + k

            if isnumber(page_source[s1 + 1:j]) and isnumber(page_source[j + 17:s2]):
                home_score = page_source[s1 + 1:j]
                away_score = page_source[j + 17:s2]
            else:
                home_team = page_source[s1 + 1:j]
                away_team = page_source[j + 17:s2]

    home_shots = num_vect[0]
    away_shots = num_vect[1]
    home_saves = num_vect[2]
    away_saves = num_vect[3]
    home_penalty = num_vect[4]
    away_penalty = num_vect[5]

    hp1score = period_list[1][0]
    hp2score = period_list[1][2]
    hp3score = period_list[1][4]
    ap1score = period_list[1][1]
    ap2score = period_list[1][3]
    ap3score = period_list[1][5]

    if len(period_list[1]) > 6:
        hp4score = period_list[1][6]
    else:
        hp4score = 0

    if len(period_list[1]) > 7:
        ap4score = period_list[1][7]
    else:
        ap4score = 0

    hp1shots = period_list[0][0]
    hp2shots = period_list[0][1]
    hp3shots = period_list[0][2]
    ap1shots = period_list[2][0]
    ap2shots = period_list[2][1]
    ap3shots = period_list[2][2]

    if len(period_list[0]) > 3:
        hp4shots = period_list[0][3]
    else:
        hp4shots = 0

    if len(period_list[2]) > 3:
        ap4shots = period_list[2][3]
    else:
        ap4shots = 0

    ap1saves = hp1shots - hp1score
    ap2saves = hp2shots - hp2score
    ap3saves = hp3shots - hp3score
    ap4saves = hp4shots - hp4score
    hp1saves = ap1shots - ap1score
    hp2saves = ap2shots - ap2score
    hp3saves = ap3shots - ap3score
    hp4saves = ap4shots - ap4score

    hp1penalty = period_list[5][0]
    hp2penalty = period_list[5][1]
    hp3penalty = period_list[5][2]
    ap1penalty = period_list[6][0]
    ap2penalty = period_list[6][1]
    ap3penalty = period_list[6][2]

    if len(period_list[5]) > 3:
        hp4penalty = period_list[5][3]
    else:
        hp4penalty = 0

    if len(period_list[6]) > 3:
        ap4penalty = period_list[6][3]
    else:
        ap4penalty = 0

    output.append(id)
    output.append(gamedate)
    output.append(home_team)
    output.append(away_team)

    output.append(home_score)
    output.append(away_score)
    output.append(home_shots)
    output.append(away_shots)
    output.append(home_saves)
    output.append(away_saves)
    output.append(home_penalty)
    output.append(away_penalty)

    output.append(hp1score)
    output.append(hp2score)
    output.append(hp3score)
    output.append(hp4score)
    output.append(ap1score)
    output.append(ap2score)
    output.append(ap3score)
    output.append(ap4score)

    output.append(hp1shots)
    output.append(hp2shots)
    output.append(hp3shots)
    output.append(hp4shots)
    output.append(ap1shots)
    output.append(ap2shots)
    output.append(ap3shots)
    output.append(ap4shots)

    output.append(hp1saves)
    output.append(hp2saves)
    output.append(hp3saves)
    output.append(hp4saves)
    output.append(ap1saves)
    output.append(ap2saves)
    output.append(ap3saves)
    output.append(ap4saves)

    output.append(hp1penalty)
    output.append(hp2penalty)
    output.append(hp3penalty)
    output.append(hp4penalty)
    output.append(ap1penalty)
    output.append(ap2penalty)
    output.append(ap3penalty)
    output.append(ap4penalty)

    return output



    # print(gameVector[i])
    # print(gamedate)
    # print(home_team)
    # print(away_team)
    # print(home_score)
    # print(away_score)
    # print(home_shots)
    # print(away_shots)
    # print(home_saves)
    # print(away_saves)
    # print(home_penalty)
    # print(away_penalty)
    # print(hp1score)
    # print(hp2score)
    # print(hp3score)
    # print(ap1score)
    # print(ap2score)
    # print(ap3score)
    # print(hp1shots)
    # print(hp2shots)
    # print(hp3shots)
    # print(ap1shots)
    # print(ap2shots)
    # print(ap3shots)
    # print(hp1saves)
    # print(hp2saves)
    # print(hp3saves)
    # print(ap1saves)
    # print(ap2saves)
    # print(ap3saves)
    # print(hp1penalty)
    # print(hp2penalty)
    # print(hp3penalty)
    # print(ap1penalty)
    # print(ap2penalty)
    # print(ap3penalty)


    # 1 Game ID
    # 2 Date

    # 3 Home team
    # 4 Away team
    # 5 Home score
    # 6 Away score
    # 7 Home shots
    # 8 Away shots
    # 9 Home saves
    # 10 Away saves
    # 11 Home penalty minutes
    # 12 Away penalty inutes

    # 13 Period one home score
    # 14 Period one away score
    # 15 Period two home score
    # 16 Period two away score
    # 17 Period three home score
    # 18 Period three away score
    # 19 Period four home score
    # 20 Period four away score

    # 21 Period one home shots
    # 22 Period one away shots
    # 23 Period two home shots
    # 24 Period two away shots
    # 25 Period three home shots
    # 26 Period three away shots
    # 27 Period four home shots
    # 28 Period four away shots

    # 29 Period one home saves
    # 30 Period one away saves
    # 31 Period two home saves
    # 32 Period two away saves
    # 33 Period three home saves
    # 34 Period three away saves
    # 35 Period four home saves
    # 36 Period four away saves

    # 37 Period one home penalty minutes
    # 38 Period one away penalty minutes
    # 39 Period two home penalty minutes
    # 40 Period two away penalty minutes
    # 41 Period three home penalty minutes
    # 42 Period three away penalty minutes
    # 43 Period four home penalty minutes
    # 44 Period four away penalty minutes


