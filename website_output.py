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

create_pre_match_analysis('2018-10-31','SHL',"BIK Karlskoga","Leksands IF","")
create_pre_match_analysis('2018-10-31','SHL',"IF Björklöven","HC Vita Hästen","")
create_pre_match_analysis('2018-10-31','SHL',"IK Oskarshamn","Västerås IK","")
create_pre_match_analysis('2018-10-31','SHL',"IK Pantern","Södertälje SK","")
create_pre_match_analysis('2018-10-31','SHL',"Karlskrona HK","Tingsryds AIF","")


#create_pre_match_analysis('2018-10-30','SHL',"Djurgårdens IF","","")

#create_pre_match_analysis('2018-10-31','HA',"BIK Karlskoga","Leksands IF","")
