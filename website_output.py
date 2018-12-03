import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from create_pre_match_analysis import create_pre_match_analysis

#create_pre_match_analysis('2018-11-22', 'SHL', "Linköping HC", "Rögle BK", "", c, conn)
#create_pre_match_analysis('2018-11-22', 'SHL', "Mora IK", "IF Malmö Redhawks", "", c, conn)
#create_pre_match_analysis('2018-11-22', 'SHL', "Örebro HK", "Luleå HF", "", c, conn)
#create_pre_match_analysis('2018-11-22', 'SHL', "Växjö Lakers HC", "Djurgårdens IF", "", c, conn)
#create_pre_match_analysis('2018-11-22', 'SHL', "HV 71", "Brynäs IF", "", c, conn)
#create_pre_match_analysis('2018-11-22', 'SHL', "Timrå IK", "Skellefteå AIK", "", c, conn)
#create_pre_match_analysis('2018-11-22', 'SHL', "Frölunda HC", "Färjestad BK", "393484", c, conn)

#create_pre_match_analysis('2018-11-22', 'SHL', "Timrå IK", "Rögle BK", "", c, conn)



#create_pre_match_analysis('2018-10-30','SHL',"Djurgårdens IF","","")

#create_pre_match_analysis('2018-10-31','HA',"BIK Karlskoga","Leksands IF","")


create_pre_match_analysis('2018-11-29','SHL',"Luleå HF","Linköping HC","", c, conn)
create_pre_match_analysis('2018-11-29','SHL',"Skellefteå AIK","Mora IK","", c, conn)
create_pre_match_analysis('2018-11-29','SHL',"Rögle BK","HV 71","", c, conn)
create_pre_match_analysis('2018-11-29','SHL',"Frölunda HC","Brynäs IF","", c, conn)
#create_pre_match_analysis('2018-11-24','SHL',"IF Malmö Redhawks","HV 71","", c, conn)
#create_pre_match_analysis('2018-11-24','SHL',"Mora IK","Linköping HC","", c, conn)
#create_pre_match_analysis('2018-11-27','SHL',"Frölunda HC","Rögle BK","", c, conn)