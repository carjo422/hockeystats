import urllib.request as urllib
from functions import find_str
from functions import get_td_content

def get_refs(id):
    gameUrl = "http://stats.swehockey.se/Game/LineUps/" + str(id)
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

    refs = ""
    rvect = ["",""]
    lines = ""
    lvect = ["",""]

    for i in range(0,len(content)):
        if content[i] == "Referee(s)":
            refs = content[i+1]
        if content[i] == "Linesmen":
            lines = content[i+1]

    a=0

    for i in range(0,len(refs)):
        if refs[i] == ",":
            rvect.append(refs[a:i])
            a=i + 2

    rvect.append(refs[a:-1])

    a = 0

    for i in range(0, len(lines)):
        if lines[i] == ",":
            lvect.append(lines[a:i])
            a = i + 2

    lvect.append(lines[a:-1])

    return [rvect, lvect]
