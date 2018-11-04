import sqlite3
conn = sqlite3.connect('hockeystats.db')
c = conn.cursor()

from create_pre_match_analysis import create_pre_match_analysis

#create_pre_match_analysis('2018-10-30','SHL',"Frölunda HC","Örebro HK","")
#create_pre_match_analysis('2018-10-30','SHL',"HV 71","Brynäs IF","")
#create_pre_match_analysis('2018-10-30','SHL',"Linköping HC","Djurgårdens IF","")
#create_pre_match_analysis('2018-10-30','SHL',"Mora IK","Rögle BK","")
#create_pre_match_analysis('2018-10-30','SHL',"Skellefteå AIK","IF Malmö Redhawks","")
#create_pre_match_analysis('2018-10-30','SHL',"Timrå IK","Luleå HF","")
#create_pre_match_analysis('2018-10-30','SHL',"Växjö Lakers HC","Färjestad BK","")

create_pre_match_analysis('2018-11-01','SHL',"Rögle BK","Växjö Lakers HC","",c, conn)
#create_pre_match_analysis('2018-11-01','SHL',"Brynäs IF","Mora IK","")
#create_pre_match_analysis('2018-11-01','SHL',"Djurgårdens IF","Linköping HC","")
#create_pre_match_analysis('2018-11-01','SHL',"Färjestad BK","Skellefteå AIK","")
#create_pre_match_analysis('2018-11-01','SHL',"Örebro HK","HV 71","")
#create_pre_match_analysis('2018-11-01','SHL',"Frölunda HC","IF Malmö Redhawks","")
#create_pre_match_analysis('2018-11-01','SHL',"Luleå HF","Timrå IK","")


#create_pre_match_analysis('2018-10-30','SHL',"Djurgårdens IF","","")

#create_pre_match_analysis('2018-10-31','HA',"BIK Karlskoga","Leksands IF","")
