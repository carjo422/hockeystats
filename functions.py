import datetime, calendar
from datetime import date

def date_diff(date1,date2):

    y1 = int(date1[0:4])
    m1 = int(date1[5:7])
    d1 = int(date1[8:10])

    y2 = int(date2[0:4])
    m2 = int(date2[5:7])
    d2 = int(date2[8:10])

    dtdiff = date(y1,m1,d1)-date(y2,m2,d2)

    return dtdiff.days


def mean_list(list,n):
    sum=0
    for i in range(0, len(list)):
        sum+= float(list[i][n])


    sum = sum / len(list)

    return sum



def isnumber(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def isfloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def find_str(s, char):
    index = 0

    if char in s:
        c = char[0]
        for ch in s:
            if ch == c:
                if s[index:index+len(char)] == char:
                    return index

            index += 1

    return -1

def get_all_numbers(string):

    list = []

    i = 0

    while i < len(string):
        if i < len(string)-1:
            if isnumber(string[i]) == True and isnumber(string[i+1]) == False:
                list.append(int(string[i]))
                i=i+1
            elif isnumber(string[i]) == True and isnumber(string[i+1]) == True:
                list.append(int(string[i:i+2]))
                i=i+2
        else:
            if isnumber(string[i]) == True:
                list.append(int(string[i]))
                i = i + 1

        i=i+1


    maxcalc=-1



    return list

def get_isolated_number(datastring, i):

    number = -1
    isolated_number = 1

    if datastring[i] == ">":
        for j in range(1,10):

            if datastring[i+j] == "<" and isolated_number == 1:
                if isnumber(datastring[i+1:i+j]):
                    number = int(datastring[i+1:i+j])
                else:
                    isolated_number = 0
                    number = -1

    return number

def get_isolated_percent(datastring, i):

    percent = -1
    isolated_number = 1

    if datastring[i] == ">":
        for j in range(1,10):

            if datastring[i+j] == "%" and isolated_number == 1:

                read_value = datastring[i+1:i+j].replace(",",".")

                if isfloat(read_value):
                    percent = float(read_value)/100
                else:
                    isolated_number = 0
                    percent = -1

    return percent

def get_period_stats(datastring, i):

    period_vector = []
    isolated_number = 1

    period_string = ""

    period_number = 0

    if datastring[i] == "(":
        for j in range(1, 25):
            if datastring[i + j] == ")" and isolated_number == 1:


                for k in range(i+1,i+j):

                    period_string = datastring[i+1:i+j]

                    period_number = 1


                    if isnumber(datastring[k]) == True or datastring[k] == ":":
                        isolated_number = 0
                    else:
                        period_number = 0
                        isolated_number = 0

    if period_number == 1:
        period_string = period_string.replace(":","A")
        period_vector = get_all_numbers(period_string)

    return period_vector

def get_td_content(string):

    content = []

    for j in range(1,len(string)-5):
        if string[j].lower() == ">":

            tag_start = 0
            k=0

            while tag_start == 0:
                k=k+1

                if j+k >= len(string):
                    tag_start = 1
                else:
                    if string[j+k] == "<":
                        tag_start = 1

            if k > 1:
                content.append(string[j+1:j+k])

    return content


def transform_date(date,n):

    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])

    day = day-n
    if day <= 0:
        month-=1
        day+=30

        if month <= 0:
            year-=1
            month+=12

    new_year = str(year)

    if month > 9:
        new_month = str(month)
    else:
        new_month = '0'+str(month)

    if day > 9:
        new_day = str(day)
    else:
        new_day = '0' + str(day)


    new_date = new_year+'-'+new_month+'-'+new_day

    return(new_date)

def get_short_team_name(team):

    if team == "IF Malmö Redhawks":
        output = ("Malmö")
    elif team == "Frölunda HC":
        output = ("Frölunda")
    elif team == "Skellefteå AIK":
        output = ("Skellefteå")
    elif team == "Växjö Lakers HC":
        output = ("Växjö")
    elif team == "HV 71":
        output = ("HV 71")
    elif team == "Rögle BK":
        output = ("Rögle")
    elif team == "Brynäs IF":
        output = ("Brynäs")
    elif team == "Timrå IK":
        output = ("Timrå")
    elif team == "Luleå HF":
        output = ("Luleå")
    elif team == "Linköping HC":
        output = ("Linköping")
    elif team == "Mora IK":
        output = ("Mora")
    elif team == "Örebro HK":
        output = ("Örebro")
    elif team == "Djurgårdens IF":
        output = ("Djurgården")
    elif team == "Färjestad BK":
        output = ("Färjestad")
    elif team == "Karlskrona HK":
        output = ("Karlskrona")

    return output