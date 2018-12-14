from model_game_shots import update_shots_model_linreg
from model_nGoals import update_nGoals_model
from model_outcome import update_outcome_model1
from model_outcome import update_outcome_model2
from model_shot_efficiency import update_efficiency_model_linreg

import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

#update_shots_model_linreg

#update_shots_model_linreg(2015,'SHL',c)
#update_shots_model_linreg(2016,'SHL',c)
update_shots_model_linreg(2017,'SHL',c)
update_shots_model_linreg(2018,'SHL',c)
update_shots_model_linreg(2019,'SHL',c)

#update_shots_model_linreg(2015,'HA',c)
#update_shots_model_linreg(2016,'HA',c)
update_shots_model_linreg(2017,'HA',c)
update_shots_model_linreg(2018,'HA',c)
update_shots_model_linreg(2019,'HA',c)

#update_efficiency_model_linreg
update_efficiency_model_linreg(2017,'SHL',c)
update_efficiency_model_linreg(2018,'SHL',c)
update_efficiency_model_linreg(2019,'SHL',c)

update_efficiency_model_linreg(2017,'HA',c)
update_efficiency_model_linreg(2018,'HA',c)
update_efficiency_model_linreg(2019,'HA',c)

#get_shots_goals_linreg

#update_nGoals_model(2015,'SHL',c)
#update_nGoals_model(2016,c)
update_nGoals_model(2017,c)
update_nGoals_model(2018,c)
update_nGoals_model(2019,c)

# update_outcome_model1

#update_outcome_model1(2015, 'SHL', c)
#update_outcome_model1(2016, 'SHL', c)
update_outcome_model1(2017, 'SHL', c)
update_outcome_model1(2018, 'SHL', c)
update_outcome_model1(2019, 'SHL', c)

#update_outcome_model1(2015, 'HA', c)
#update_outcome_model1(2016, 'HA', c)
update_outcome_model1(2017, 'HA', c)
update_outcome_model1(2018, 'HA', c)
update_outcome_model1(2019, 'HA', c)

# update_outcome_model2

#update_outcome_model2(2015, 'SHL', c)
#update_outcome_model2(2016, 'SHL', c)
update_outcome_model2(2017, 'SHL', c)
update_outcome_model2(2018, 'SHL', c)
update_outcome_model2(2019, 'SHL', c)

#update_outcome_model2(2015, 'HA', c)
#update_outcome_model2(2016, 'HA', c)
update_outcome_model2(2017, 'HA', c)
update_outcome_model2(2018, 'HA', c)
update_outcome_model2(2019, 'HA', c)



