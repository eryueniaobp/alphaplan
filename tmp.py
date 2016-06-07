__author__ = 'baidu'
import os
from data_transform import *

config = ConfigParser.RawConfigParser()
config.read('alpha.ini')
poi_data = {}

dir =  os.path.dirname(os.path.realpath(__file__))
load_poi(dir+'/' + config.get('unittest', 'poi_data'),poi_data)
# print poi_data
for key in poi_data:
    print get_poi_feas(key , poi_data)


print find_nearest_district(poi_data,'c4ec24e0a58ebedaa1661e5c09e47bb5')