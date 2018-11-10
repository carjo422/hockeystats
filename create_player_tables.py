import pandas as pd
import openpyxl
from pandas import ExcelWriter


def get_player_data(team, gamedate, seasonYear, serie, c, conn):

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


    #print(players2)

    current_season = pd.DataFrame(columns=['Forname', 'Surname', 'Position', 'Handle', 'Length', 'Weight', 'Games', 'Goals', 'Assist', 'Plus', 'Minus', 'InPP', 'InBP', 'Line1%', 'Line2%','Line3%', 'Line4%', 'Extra%'])
    past_seasons = pd.DataFrame(columns=['Forname', 'Surname', 'Position', 'Handle', 'Length', 'Weight', 'Games', 'Goals', 'Assist', 'Plus', 'Minus', 'InPP', 'InBP', 'Line1%', 'Line2%','Line3%', 'Line4%', 'Extra%'])

    for i in range(0,len(players2)):

        forname = players2['Forname'][i]
        surname = players2['Surname'][i]
        personnr = players2['Personnr'][i]

        c.execute("SELECT POSITION, HANDLE, LENGHT, WEIGHT FROM ROSTERS WHERE FORNAME = ? AND SURNAME = ? AND PERSONNR = ? ORDER BY SEASONID DESC",[forname, surname, personnr])
        rst = c.fetchall()

        position = ""
        handle = ""
        weight = ""
        length = ""

        if len(rst) > 0:
            position = rst[0][0]
            handle = rst[0][1]
            weight = rst[0][2]
            length = rst[0][3]

        c.execute("""SELECT FORNAME,
                            SURNAME,
                            COUNT(GAMEID),
                            SUM(GOALS),
                            SUM(ASSISTS),
                            SUM(PLUS),
                            SUM(MINUS),
                            SUM(CAST(INPOWERPLAY AS FLOAT))/COUNT(GAMEID),
                            SUM(CAST(INBOXPLAY AS FLOAT))/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID)
                        FROM
                            LINEUPS
                        WHERE
                            FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND SEASONID = ? AND GAMEDATE < ?
                        GROUP BY
                            FORNAME, SURNAME, PERSONNR""", ['1st Line', '2nd Line', '3rd Line', '4th Line', 'Extra players', forname, surname, personnr, seasonYear, gamedate])

        sts = c.fetchall()

        if len(sts) > 0:
            current_season = current_season.append({'Forname': sts[0][0], 'Surname': sts[0][1], 'Position': position, 'Handle': handle, 'Length': length, 'Weight': weight, 'Games': sts[0][2], 'Goals': sts[0][3], 'Assist': sts[0][4], 'Plus': sts[0][5], 'Minus': sts[0][6], 'InPP': sts[0][7], 'InBP': sts[0][8], 'Line1%': sts[0][9], 'Line2%': sts[0][10], 'Line3%': sts[0][11], 'Line4%': sts[0][12], 'Extra%': sts[0][13]},ignore_index=True)

        c.execute("""SELECT FORNAME,
                            SURNAME,
                            COUNT(GAMEID),
                            SUM(GOALS),
                            SUM(ASSISTS),
                            SUM(PLUS),
                            SUM(MINUS),
                            SUM(CAST(INPOWERPLAY AS FLOAT))/COUNT(GAMEID),
                            SUM(CAST(INBOXPLAY AS FLOAT))/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID),
                            SUM(CASE WHEN POSITION = ? THEN CAST(1 AS FLOAT) ELSE 0 END)/COUNT(GAMEID)
                        FROM
                            LINEUPS
                        WHERE
                            FORNAME = ? AND SURNAME = ? AND PERSONNR = ? AND SEASONID < ? AND GAMEDATE < ? AND SERIE = ?
                        GROUP BY
                            FORNAME, SURNAME, PERSONNR""", ['1st Line', '2nd Line', '3rd Line', '4th Line', 'Extra players', forname, surname, personnr, seasonYear, gamedate, serie])

        sts = c.fetchall()

        if len(sts) > 0:
            past_seasons = past_seasons.append({'Forname': sts[0][0], 'Surname': sts[0][1], 'Position': position, 'Handle': handle, 'Length': length, 'Weight': weight, 'Games': sts[0][2], 'Goals': sts[0][3], 'Assist': sts[0][4],'Plus': sts[0][5], 'Minus': sts[0][6], 'InPP': sts[0][7], 'InBP': sts[0][8], 'Line1%': sts[0][9],'Line2%': sts[0][10], 'Line3%': sts[0][11], 'Line4%': sts[0][12], 'Extra%': sts[0][13]}, ignore_index=True)


    writer = ExcelWriter('Exports/player_data_' + gamedate + '.xlsx')

    current_season.to_excel(writer, team + '_current_season')
    past_seasons.to_excel(writer, team + '_past_seasons')

    writer.save()

    return current_season, past_seasons