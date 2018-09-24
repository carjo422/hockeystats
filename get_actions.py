import urllib.request as urllib
from functions import find_str
from functions import get_td_content
from functions import isnumber
from functions import get_all_numbers

def get_actions(id, audience, venue, season, team1, team2,c):
    gameUrl = "http://stats.swehockey.se/Game/Events/" + str(id)
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

    content = get_td_content(page_source)

    period = 0
    events = []

    for i in range(0, len(content)):

        stn = content[i]

        if "Overtime" in stn:
            period = 4
        elif "3rd" in stn:
            period = 3
        elif "2nd" in stn:
            period = 2
        elif "1st" in stn:
            period = 1

        if "%" in content[i] and "(" in content[i+1] and ")" in content [i+1] and "/" in content[i+1]:
            #print(content[i+1])

            [saves,shots] = get_all_numbers(content[i+1])

            event = create_goalie_event(id, period, content[i-2:i+1], shots, saves, audience, venue, season)
            events.append(event)


        if isnumber(content[i][0:2]) and isnumber(content[i][3:5]) and content[i][2] == ":":

            event = create_event(id, period, content[i-1:i+6], audience, venue, season)
            events.append(event)

            if event[3] == "Goal":

                extra = event[8]

                for j in range(5,9):
                    if isnumber(content[i+j][0]) and content[i+j].find(".") > 0 and content[i + j].find(".") < 5:
                        event = create_assist_event(content[i+j], event, audience, venue, season, extra)
                        events.append(event)

                    if "Neg." in content[i+j]:
                        numbers = (get_all_numbers(content[i + j]))

                        for k in range(0,len(numbers)):
                            event = create_plus_minus_event(event, -1, numbers[k], audience, venue, season, extra)
                            events.append(event)

                    if "Pos." in content[i + j]:
                        numbers = (get_all_numbers(content[i + j]))

                        for k in range(0, len(numbers)):
                            event = create_plus_minus_event(event, 1, numbers[k], audience, venue, season, extra)
                            events.append(event)


    home_team_short = events[-1][4]

    for i in range(0,len(events)):
        if events[i][3] != -1:
            if events[i][4] == home_team_short:
                events[i][4] = team1
            else:
                events[i][4] = team2
        else:
            if events[i][4] == home_team_short:
                events[i][4] = team2
            else:
                events[i][4] = team1

        if events[i][3] in [-1,1]:
            c.execute("SELECT FORNAME, SURNAME FROM lineups where GAMEID = ? and TEAM = ? and NUMBER = ?",
                      [events[i][0], events[i][4], events[i][5]])
            player_name = c.fetchall()

            events[i][6]=""
            events[i][7]=""

            try:
                events[i][6] = player_name[0][1]
            except IndexError:
                pass
            try:
                events[i][7] = player_name[0][0]
            except IndexError:
                pass

    #print(events)
    return events



def create_event(id, period, content, audience, venue, season):

    n=0

    output0 = id
    output1 = period
    output2 = content[1]

    output8 = ""
    output9 = ""
    output10 = audience
    output11 = venue
    output12 = season

    if content[2] in ['GK Out', 'GK In', 'TO']:
        output3 = content[2]
    elif content[2] in ['2 min', '5 min', '10 min', '20 min']:
        output3 = "Penalty"
        output9 = content[2][0:2]
    elif "-" in content[2] and "(" in content[2] and ")" in content[2]:
        output3 = "Goal"
    else:
        output3 = content[2]

    if "PP" in content[2]:
        output8 = "PP"
    if "SH" in content[2]:
        output8 = "SH"

    if "ENG" in content[3]:
        output9 = "ENG"
        n=1

    output4 = content[3+n]

    if content[2] not in ['TO']:
        content[4+n] = content[4+n].replace(" ", "")

        p1 = content[4+n].find(".")
        p2 = content[4+n].find(",")

        output5 = content[4+n][0:p1]
        output6 = content[4+n][p1+1:p2]
        output7 = content[4+n][p2+1:len(content[4+n])]


    else:
        output5 = ""
        output6 = ""
        output7 = ""

    if output3 == "Penalty":
        output8 = content[5+n]

    output = [output0, output1, output2, output3, output4, output5, output6, output7, output8, output9, output10, output11, output12]

    return output

def create_assist_event(content, event, audience, venue, season,extra):
    output0 = event[0]
    output1 = event[1]
    output2 = event[2]
    output3 = "Assist"
    output4 = event[4]

    content = content.replace(" ", "")

    p1 = content.find(".")
    p2 = content.find(",")

    output5 = content[0:p1]
    output6 = content[p1+1:p2]
    output7 = content[p2+1:len(content)]

    output8 = extra
    output9 = ""
    output10 = audience
    output11 = venue
    output12 = season

    output = [output0, output1, output2, output3, output4, output5, output6, output7, output8, output9, output10, output11, output12]

    return output

def create_plus_minus_event(event, sign, number, audience, venue, season,extra):
    output0 = event[0]
    output1 = event[1]
    output2 = event[2]
    output3 = sign
    output4 = event[4]
    output5 = number
    output6 = ""
    output7 = ""
    output8 = ""

    if sign == -1:
        if extra == 'PP':
            output8 = 'SH'
        elif extra == 'SH':
            output8 = 'PP'
    else:
        output8=extra

    output9 = ""
    output10 = audience
    output11 = venue
    output12 = season

    output = [output0, output1, output2, output3, output4, output5, output6, output7, output8, output9, output10, output11, output12]

    return output

def create_goalie_event(id, period, content, shots, saves, audience, venue, season):

    output0 = id
    output1 = ""
    output2 = ""
    output3 = "Keeper stat"
    output4 = content[0]

    content[1] = content[1].replace(" ", "")

    p1 = content[1].find(".")
    p2 = content[1].find(",")

    output5 = content[1][0:p1]
    output6 = content[1][p1 + 1:p2]
    output7 = content[1][p2 + 1:len(content[1])]


    output8 = shots
    output9 = saves
    output10 = audience
    output11 = venue
    output12 = season

    output = [output0, output1, output2, output3, output4, output5, output6, output7, output8, output9, output10, output11, output12]

    return output