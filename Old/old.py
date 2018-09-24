#c.execute("""CREATE TABLE roster (
#                ID integer,
#                SEASONID integer,
#                TEAM TEXT,
#                NUMBER integer,
#                FORNAME TEXT,
#                SURNAME TEXT,
#                POSITION TEXT)""")

#Create roster table

    for i in range(0,len(lineups)):
        c.execute("SELECT ID as ID FROM roster where TEAM = ? and NUMBER = ? and FORNAME = ? and SURNAME = ? and SEASONID = ?", [lineups[i][1],lineups[i][2],lineups[i][3],lineups[i][4],seasonYear])
        hits = c.fetchall()

        c.execute("SELECT ID as ID FROM roster")
        ids = c.fetchall()

        if len(ids) > 0:
            id = max(ids)[0]+1
        else:
            id = 1

        if len(hits) == 0:

            if lineups[i][5] == "Goalies":
                position = "G"
            else:
                position = "D/F"

            c.execute("""INSERT INTO
                roster (
                    ID,SEASONID,TEAM,NUMBER,FORNAME,SURNAME,POSITION)
                VALUES
                    (?,?,?,?,?,?,?)""",
                      (id,seasonYear,lineups[i][1],lineups[i][2],lineups[i][3],lineups[i][4],position))

        else:
            pass

    conn.commit()