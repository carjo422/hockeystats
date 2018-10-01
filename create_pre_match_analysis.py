import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from pre_match_functions import get_form
from pre_match_functions import get_player_form
from pre_match_functions import get_team_schedule

def create_pre_match_analysis(gamedate, serie, hometeam, awayteam):

    seasonYear = int(gamedate[0:4])
    if int(gamedate[5:7]) > 6:
        seasonYear += 1

    [form, offForm, defForm, points5, goals5, conc5, points1, goals1, conc1] = get_form(hometeam,seasonYear,gamedate,c)
    print([form, offForm, defForm, points5, goals5, conc5, points1, goals1, conc1])

    [form, offForm, defForm, points5, goals5, conc5, points1, goals1, conc1] = get_form(awayteam, seasonYear,gamedate,c)
    print([form, offForm, defForm, points5, goals5, conc5, points1, goals1, conc1])

    get_player_form(hometeam, seasonYear, gamedate, c)

    print(get_team_schedule(hometeam, seasonYear, gamedate, c))
    print(get_team_schedule(awayteam, seasonYear, gamedate, c))














create_pre_match_analysis('2018-10-02','SHL','Linköping HC','Brynäs IF')