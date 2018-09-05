import urllib.request as urllib
from functions import find_str
from functions import get_td_content
from functions import isnumber

def get_actions(id, team1, team2):
    gameUrl = "http://stats.swehockey.se/Game/Events/" + str(id)
    response = urllib.urlopen(gameUrl)
    page_source = str(response.read())

    page_source = page_source.replace("\\xc3\\xa5", "å")
    page_source = page_source.replace("\\xc3\\xa4", "ä")
    page_source = page_source.replace("\\xc2\\xa0", " ")
    page_source = page_source.replace("\\xc3\\xa9", "é")
    page_source = page_source.replace("\\xc3\\xb6", "ö")
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

        if isnumber(content[i][0:2]) and isnumber(content[i][3:5]) and content[i][2] == ":":

            event = create_event(id, period, content[i-1:i+5])
            events.append(event)

            if event[3] == "Goal":
                pass#event = create_goal_event(id,period,content[i-1:i+9])

            #events.append(event)

    print(events)


def create_event(id, period, content ):

    output0 = id
    output1 = period
    output2 = content[1]

    if content[2] in ['GK Out', 'GK In', 'TO']:
        output3 = content[2]
    elif content[2] in ['2 min', '5 min', '10 min', '20 min']:
        output3 = "Penalty"
    elif "-" in content[2] and "(" in content[2] and ")" in content[2]:
        output3 = "Goal"
    else:
        output3 = content[2]

    output4 = content[3]

    if content[2] not in ['TO']:
        content[4] = content[4].replace(" ", "")

        p1 = content[4].find(".")
        p2 = content[4].find(",")

        output5 = content[4][0:p1]
        output6 = content[4][p1:p2]
        output7 = content[4][p2:len(content[4])]


    else:
        output5 = ""
        output6 = ""
        output7 = ""

    if output3 == "Penalty":
        output8 = content[5]
    else:
        output8 = ""

    output = [output0, output1, output2, output3, output4, output5, output6, output7, output8]

    return output

def create_goal_event(id, period, content ):
    pass