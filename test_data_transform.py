import  unittest,os
from data_transform import *
class TestDataTransform(unittest.TestCase):
    def setUp(self):

        self.dir =  os.path.dirname(os.path.realpath(__file__))

        self.config = ConfigParser.RawConfigParser()
        self.config.read('alpha.ini')
    def test_expand_cross_feature(self):
        kvmap = {
            'dishash': 'dishash',
            'slice': '2',
            'dayofweek': '4' ,
            'is_workday': '0' ,
            'wea': '1'

        }
        idmap = {}
        curid = 1
        curid,cfvec = expand_cross_feature(kvmap,idmap,curid)
        print cfvec
        cnt  = len(cross_feas)
        for i in range(cnt):
            key = '{id}:1'.format(id=i+1)
            self.assertTrue( key in  cfvec )

    def test_parse_time_slice(self):
        print parse_time_slice("23:59:59")
        print parse_time_slice("00:09:00")
        self.assertEqual(parse_time_slice("23:59:00") ,144)
        self.assertEqual(parse_time_slice("00:09:00") ,1)
        pass
    def test_distance(self):
        self.assertEqual(distance("2016-01-02-1" , "2016-01-02-4") , -3 * 10 * 60  )
        self.assertEqual(distance("2016-01-02-1" , "2016-01-01-143") , 2 * 10 * 60 )
    def test_iter_slice(self):
        for prev, next in iter_slice('2016-01-09', 1):
            self.assertEqual(prev, '2016-01-08-144')
            self.assertEqual(next , '2016-01-09-2')
            break

        for prev,next in iter_slice('2016-01-09', 144):
            self.assertEqual(prev, '2016-01-09-143')
            self.assertEqual(next , '2016-01-10-1')
            break

    def test_slice_to_hour(self):
        self.assertEqual(slice_to_hour(1), '00:09')
        self.assertEqual(slice_to_hour(144), '23:59')
    def test_load_poi(self):
        poi_data =  {}
        load_poi(self.dir+'/' + self.config.get('unittest', 'poi_data'),poi_data)
        pass
    def test_load_traffic(self):
        trf_data =  {}
        load_traffic(self.dir+'/' + self.config.get('unittest', 'traffic_data'),trf_data)
        pass
    def test_load_weather(self):
        wea_data = {}
        load_weather(self.dir+'/' + self.config.get('unittest','weather_data'),wea_data)
        pass
    def test_load_order(self):
        print 'key'
        pass
    def test_get_poi_feas(self):
        poi_data =  {}
        load_poi(self.dir+'/' + self.config.get('unittest', 'poi_data'),poi_data)
        for key in poi_data:
            print 'poi-feas' , get_poi_feas(key , poi_data)
    def test_get_traffic_feas(self):
        trf_data =  {}
        load_traffic(self.dir+'/' + self.config.get('unittest', 'traffic_data'),trf_data)
        for key in trf_data:
            print key  , get_traffic_feas(key,trf_data)
    def test_get_nearest_weather_key(self):
        wea_data = {}
        load_weather(self.dir+'/' + self.config.get('unittest','weather_data'),wea_data)
        key =  nearest_weather_key('2016-01-19-105' , wea_data)
        print key
        key = nearest_weather_key('2016-01-19-49',wea_data)
        print key
    def test_get_weather_feas(self):
        wea_data = {}
        load_weather(self.dir+'/' + self.config.get('unittest','weather_data'),wea_data)
        for key in wea_data:
            day =  key[0:10]
            break
        keys = [ day +'-' + str(i+1) for i in range(144)]
        for key in keys:
            print key ,get_weather_feas(key,wea_data)

    def test_get_traffic_feas(self):
        trf_data =  {}
        load_traffic(self.dir+'/' + self.config.get('unittest', 'traffic_data'),trf_data)
        k = ''
        for key in trf_data:
            k = key
            break
        ws = k.split('-')

        keys = [ '{dishash}-{day}-{slice}'.format(dishash=ws[0],day=ws[1]+'-'+ws[2]+'-'+ws[3] ,slice=i+1) for i in range(144) ]
        for key in keys:
            print key,get_traffic_feas(key ,trf_data)


if __name__ == '__main__':
    unittest.main()