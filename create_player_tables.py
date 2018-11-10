import pandas as pd

def get_player_data(team, gamedate, seasonYear, c, conn):

    #Get all players in current team

    c.execute("SELECT DISTINCT FORNAME, SURNAME, PERSONNR FROM LINEUPS WHERE TEAM = ? AND SEASONID = ?",[team, seasonYear])
    players1 = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr'])

    c.execute("SELECT FORNAME, SURNAME, PERSONNR FROM ROSTERS WHERE TEAM = ? AND SEASONID = ?",[team, seasonYear])
    players2 = pd.DataFrame(c.fetchall(), columns = ['Forname','Surname','Personnr'])


    for i in range(0,len(players1)):

        add_player = 1

        for j in range(0,len(players2)):

            if players1['Forname'][i] == players2['Forname'][j] and players1['Surname'][i] == players2['Surname'][j]:

                add_player = 0

            if players1['Personnr'][i] == players2['Personnr'][j] and players1['Personnr'][i] != "":

                if players1['Forname'][i] == players2['Forname'][j] and players1['Surname'][i][0:2] == players2['Surname'][j][0:2]:
                    add_player = 0

                if players1['Surname'][i] == players2['Surname'][j] and players1['Forname'][i][0:3] == players2['Forname'][j][0:3]:
                    add_player = 0

        if add_player == 1:

            players2 = players2.append({'Forname': players1['Forname'][i], 'Surname': players1['Surname'][i], 'Personnr': players1['Personnr'][i]},ignore_index=True)


    print(players2)


    #c.execute("SELECT FORNAME, SURNAME, POSITION, COUNT(GAMEID), SUM(GOALS), SUM(ASSIST), SUM(PLUS), SUM(MINUS), SUM(INPOWERPLAY)/COUNT(GAMEID), SUM(INBOXPLAY)/COUNT(GAMEID) FROM LINEUPS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ?",[forname, surname, personnr])

    #"Goalies"
    #"Goalies"
    #"1st Line"
    #"1st Line"
    #"1st Line"
    #"1st Line"
    #"1st Line"
    #"2nd Line"
    #"2nd Line"
    #"2nd Line"
    #"2nd Line"
    #"2nd Line"
    #"3rd Line"
    #"3rd Line"
    #"3rd Line"
    #"3rd Line"
    #"3rd Line"
    #"4th Line"
    #"4th Line"
    #"4th Line"
    #"4th Line"
    #"Extra players"

    return players1,players2