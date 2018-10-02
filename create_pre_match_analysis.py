import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from pre_match_functions import get_form
from pre_match_functions import getOdds1X2
from pre_match_functions import getOdds55
from pre_match_functions import get_player_form
from pre_match_functions import get_team_schedule
from pre_match_functions import get_offence_info
from calcFunctions import calculate_team_strength

def create_pre_match_analysis(gamedate, serie, hometeam, awayteam):

    seasonYear = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        seasonYear += 1


    [form, offForm1, defForm1, points5, hgoals5, conc5, points3, hgoals3, hgoals1, points1, hgoals1, conc1] = get_form(hometeam,seasonYear,gamedate,c)
    [form, offForm2, defForm2, points5, agoals5, conc5, points3, agoals3, agoals1, points1, agoals1, conc1] = get_form(awayteam, seasonYear,gamedate,c)




    c.execute("SELECT gamedate from teamgames where team = ? order by gamedate DESC",[hometeam])
    htd = c.fetchall()
    gamedate_pre_h = htd[0][0]

    c.execute("SELECT gamedate from teamgames where team = ? order by gamedate DESC", [awayteam])
    atd = c.fetchall()
    gamedate_pre_a = atd[0][0]

    [home_score, home_points, home_season_points, home_player_score_final] = calculate_team_strength(hometeam, gamedate_pre_h, c)
    [away_score, away_points, away_season_points, away_player_score_final] = calculate_team_strength(awayteam, gamedate_pre_a, c)

    [odds1, oddsX, odds2] = getOdds1X2(home_score,away_score)
    [prob4, prob5, prob6] = getOdds55(offForm1, defForm1, offForm2, defForm2)

    [fss, lgs] = (get_player_form(hometeam, seasonYear, gamedate, c))

    # Offence
    off_info = get_offence_info(hometeam, offForm1, hgoals5, hgoals3, hgoals1, fss, lgs)
    # Defence
    # Goalie
    # Powerplay
    # Boxplay
    # Overall

    #Goal scorers
    #Målvakt
    #Bäst form
    #Svag form
    #Största stjärnor
    #To score

    schedule_home = (get_team_schedule(hometeam, seasonYear, gamedate, c))
    schedule_away = (get_team_schedule(awayteam, seasonYear, gamedate, c))









create_pre_match_analysis('2018-10-02','SHL','Linköping HC','Brynäs IF')
create_pre_match_analysis('2018-10-02','SHL','Skellefteå AIK','Växjö Lakers HC')
create_pre_match_analysis('2018-10-02','SHL','IF Malmö Redhawks','Frölunda HC')

if 1 == 2:

    #TEST DATA ON TWO SEASONS

    c.execute("SELECT GAMEID, SEASONID, SERIE FROM SCHEDULE WHERE (SEASONID = ? OR SEASONID = ?) AND SERIE = ?",[2017,2018,'SHL'])
    testGames = c.fetchall()

    for i in range(0, len(testGames)):
        c.execute("SELECT GAMEID, HOMETEAM, AWAYTEAM, HSCORE1 + HSCORE2 + HSCORE3 as GOALS1, ASCORE1 + ASCORE2 + ASCORE3 as GOALS2 FROM STATS WHERE GAMEID = ?",[testGames[i][0]])
        scoreStats = c.fetchall()

        if scoreStats[0][3] > scoreStats[0][4]:
            outcome = 1
        elif scoreStats[0][3] < scoreStats[0][4]:
            outcome = 3
        else:
            outcome = 2

        tscore = scoreStats[0][3] + scoreStats[0][4]

        c.execute("SELECT SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?",[testGames[i][0],scoreStats[0][1]])
        hscore = c.fetchall()
        c.execute("SELECT SCORE, FORM_SCORE, LAST_SEASONS_SCORE, PLAYER_SCORE FROM TEAMSCORE WHERE GAMEID = ? AND TEAM = ?",[testGames[i][0], scoreStats[0][2]])
        ascore = c.fetchall()


        c.execute("SELECT GAMEID FROM TEST_DATA_GAME WHERE GAMEID = ?",[testGames[i][0]])
        chk = c.fetchall()

        if len(chk) > 0:
            pass
        else:
            c.execute("INSERT INTO TEST_DATA_GAME (GAMEID, OUTCOME, HGOALS, AGOALS, TGOALS, HSCORE, HFORM, HLAST, HPLAYER, ASCORE, AFORM, ALAST, APLAYER) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",[testGames[i][0],outcome, scoreStats[0][3], scoreStats[0][4], tscore, hscore[0][0], hscore[0][1], hscore[0][2], hscore[0][3], ascore[0][0], ascore[0][1], ascore[0][2], ascore[0][3]])

        conn.commit()