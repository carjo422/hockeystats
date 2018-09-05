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

                if j+k > len(string):
                    tag_start = 1
                else:
                    if string[j+k] == "<":
                        tag_start = 1

            if k > 2:
                content.append(string[j+1:j+k])

    return content




