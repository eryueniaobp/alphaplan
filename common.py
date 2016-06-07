__author__ = 'baidu'
import datetime,logging
sparse_feas = [
    'dayofweek' ,'is_workday','slice','dishash','wea'
]


def binary_gap(val, divide_val):
    if float(val) < float(divide_val) :
        return -1
    else:
        return 1
def parse_dayofweek(day):
    return datetime.datetime.strptime(day, '%Y-%m-%d').weekday()
def is_workday2(day):
    if  datetime.datetime.strptime(day, '%Y-%m-%d').weekday() >= 5:
        return 0 
    if day == '2016-01-01':
        return 0 #new year holiday
    return 1 
def transform_value(k,val):
    if k == 'temp':
        return int(float(val)/2)
    if k == 'pm25':
        return int(float(val)/5)

    if k[0:2] == 'tf':
        return int(float(val)/5)
    return val

useful_single_feas = [
    'poi', 
    'dayofweek' ,'is_workday','slice','dishash',
    'wea','pm25','temp', 
    'tf1','tf2','tf3','tf4',

    'auto_reg',

    'dis-slice-temp',
    'dis-slice-pm25',
    'dis-slice-tf1',
    'dis-slice-tf2',
    'dis-slice-tf3',
    'dis-slice-tf4',

]

useful_single_feas = ['auto_reg']

def slice_to_hour(slice):
    slice =int(slice)
    return "{hour}:{minute}".format(hour=str((slice-1)/6).zfill(2)  ,  minute =  str((slice-1)%6 * 10 + 9).zfill(2) )

# 2016-01-01 21:56:29
def parse_time_slice(hourstr):
    hour ,min , sec = hourstr.strip().split(':')
    hour = int(hour)
    min = int(min)
    sec = int(sec)
    return hour * 6 + min/10 +1
def iter_prev_dayslice(dayslice, num):
    day = dayslice[0:10]
    slice = dayslice.split('-')[-1]
    hourmin = slice_to_hour(slice)

    start_time = datetime.datetime.strptime(day+'-' + hourmin , '%Y-%m-%d-%H:%M')
    for i in range(num):
        curtime =  (start_time - datetime.timedelta(seconds=10*60*(i+1)))
        strt = curtime.strftime('%Y-%m-%d-%H:%M:%S')

        yield strt[0:10]+'-' + str(parse_time_slice(strt[11:]))
# todo : add dayofweek to key .
def build_continous_fea(kvmap):
    #build- temp
    key = 'TE{dis}-{slice}'.format(
        dis=kvmap['dishash'],
        slice=kvmap['slice'],
        )
    value = kvmap['temp']
    kvmap[key] = value

    key = 'P{dis}-{slice}'.format(
        dis=kvmap['dishash'],
        slice=kvmap['slice'],
    )
    value = kvmap['pm25']
    kvmap[key] = value

    key = 'TF1{dis}-{slice}'.format(
        dis=kvmap['dishash'],
        slice=kvmap['slice'],
    )
    value = kvmap.get('tf1','0')
    kvmap[key] = value


    key = 'TF2{dis}-{slice}'.format(
        dis=kvmap['dishash'],
        slice=kvmap['slice'],
    )
    value = kvmap.get('tf2','0')
    kvmap[key] = value

    key = 'TF3{dis}-{slice}'.format(
        dis=kvmap['dishash'],
        slice=kvmap['slice'],
    )
    value = kvmap.get('tf3','0')
    kvmap[key] = value


    key = 'TF4{dis}-{slice}'.format(
        dis=kvmap['dishash'],
        slice=kvmap['slice'],
    )
    value = kvmap.get('tf4','0')
    kvmap[key] = value

def date2key(day):
    return day.strftime('%Y-%m-%d') + '-' + str(parse_time_slice(day.strftime('%H:%M:%S')))

def iter_slice(day,slice):
    slice = int(slice)
    hour = slice_to_hour(slice)
    # print day+ ':' + hour
    cur = datetime.datetime.strptime(day+ ':' + hour , '%Y-%m-%d:%H:%M')

    cnt = 1
    while cnt < 144 :

        prev = cur - datetime.timedelta(minutes=cnt*10)
        next = cur + datetime.timedelta(minutes=cnt*10)
        #build key
        yield date2key(prev) ,date2key(next)
        cnt +=1
def nearest_weather_key(key,weather_data):
    day = key[0:10]
    slice = key[11:]

    for prev , next in iter_slice(day ,slice):
        if next in weather_data:
            return next
        if prev in weather_data:
            return prev
    return None
def nearest_traffic_key(key , trf_data):
    ws = key.split('-')
    dishash = ws[0]

    day = ws[1]+'-'+ws[2]+'-'+ws[3]
    slice = int(ws[4])

    for prev ,next in iter_slice(day,slice):
        prev_key = dishash +'-' + prev
        next_key = dishash +'-'+ next
        if next_key in trf_data:
            return next_key
        if prev_key in trf_data:
            return prev_key
    return None
def get_weather_feas(key , weather_data):
    # key = build_weather_key(day,hour)
    if key not in weather_data:
        # raise  KeyError('the key is not in the weather data')

        near_key  = nearest_weather_key(key ,weather_data)
        # print 'nearest = ' + near_key
        if near_key is None:
            logging.warn(key + ' is not the weather data')
            return []
        key = near_key

    wea_feas = [ ]
    for k in weather_data[key]:
        v = weather_data[key][k]
        wea_feas.append('{k}={v}'.format(
            k = k ,
            v = v

        ))
    return wea_feas
trf_miss_key  =set()
def get_traffic_feas(key ,traffic_data):

    if key not in traffic_data:
        # raise KeyError('The key is not in the traffic_data')
        # logging.warn(key + ' is not in the traffic_data')
        near_key = nearest_traffic_key(key ,traffic_data)
        # print 'near trf key=' , key
        if near_key is None:
            dishash =key.split('-')[0]
            if  dishash not in trf_miss_key:
                logging.warn(dishash + ' is not in the traffic_data')
                trf_miss_key.add(dishash)
            return []
        key  = near_key
    trf_feas = []

    noise_keys = ['cnt']
    for k in traffic_data[key]:
        if k in noise_keys:
            continue
        v=   traffic_data[key][k]
        trf_feas.append('{k}={v}'.format(
            k= k ,
            v = v ,
        ))
    return trf_feas

#auto regression
def build_auto_regression_fea(dishash, dayslice , trend_map,sup_map , traffic_data, weather_data) :
    
    #return []
    vec = []
    key = 'R'+str(parse_dayofweek(dayslice[0:10]))+'-'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .
    key1 = 'RW'+str(is_workday2(dayslice[0:10]))+'-'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .
    key2 = 'RD'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .

    #traffic
    key3 = 'RT'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .
    key4 = 'RP'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .
    key5 = 'RP'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .
    #weather
    key6 = 'RE'+dishash + '-' + dayslice.split('-')[-1] # 'R' to avoid poi sparse feature .
    i = 1
    for ds in iter_prev_dayslice(dayslice , 3):
        ckey = key + '-' + str(i)
        i+=1

        val = -1
        if dishash in trend_map:
            if ds in trend_map[dishash]:
                val = trend_map[dishash][ds]
        vec.append('{ckey}={val}'.format(ckey=ckey,val=val))
        vec.append('{ckey}={val}'.format(ckey=key1+'-'+str(i),val=val))
        vec.append('{ckey}={val}'.format(ckey=key2+'-'+str(i),val=val))

        vec.append('{key}={val}'.format(key=key+'-sup', val = sup_map[dishash].get(ds,1)))
        vec.append('{key}={val}'.format(key=key1+'-sup', val = sup_map[dishash].get(ds,1)))
        vec.append('{key}={val}'.format(key=key2+'-sup', val = sup_map[dishash].get(ds,1)))

        #build weather and tf

        traffic_feas = get_traffic_feas( dishash +'-' + ds , traffic_data)
        weather_feas = get_weather_feas( ds , weather_data)

        pre=  'RT'+dishash + '-' + dayslice.split('-')[-1] + '-' + str(i)
        pre2= 'RT' + str(is_workday2(dayslice[0:10])) + '-' + dishash + '-' + dayslice.split('-')[-1] + '-' + str(i)
        for k in traffic_feas:
            vec.append(pre+ k )
            vec.append(pre2+ k )

        pre = 'RE'+dishash + '-' + dayslice.split('-')[-1] + '-' + str(i)
        pre2 = 'RE'+str(is_workday2(dayslice[0:10])) + '-' + dishash + '-' + dayslice.split('-')[-1] + '-' + str(i)
        for k in weather_feas:
            vec.append(pre+k)
            vec.append(pre2+k)


        # special:  51 d4ec2125aff74eded207d2d915ef682f  gap,total-gap ,gap/total-gap

        special = 'RC' + dishash + '-' + dayslice.split('-')[-1] + '-' +str(i)

        spe_gap = trend_map['d4ec2125aff74eded207d2d915ef682f'].get(ds,1)
        total_gap = trend_map['TOTAL'].get(ds,1)
        spe_ratio = spe_gap/total_gap
        vec.append('{key}={val}'.format(key = special +'spe' , val = spe_gap))
        vec.append('{key}={val}'.format(key = special +'total' , val = total_gap))
        vec.append('{key}={val}'.format(key = special +'ratio' , val = spe_ratio))






    return vec


# Filter poi.
def filter_fea(k,v):


    vec = [ str(i) for i in range(10)]
    if k[0] in vec:
        k = 'poi'
    if k[0] == 'R':
        k = 'auto_reg'
    if k[0:2] == 'TE':
        k = 'dis-slice-temp'
    if k[0] == 'P':
        k = 'dis-slice-pm25'

    if k[0:3] == 'TF1':
        k = 'dis-slice-tf1'
    if k[0:3] == 'TF2':
        k = 'dis-slice-tf2'
    if k[0:3] == 'TF3':
        k = 'dis-slice-tf3'
    if k[0:3] == 'TF4':
        k = 'dis-slice-tf4'


    return k not in useful_single_feas
cross_feas = []
_cross_feas = [
    'dishash&slice',
    'dishash&slice&dayofweek',
    'dishash&slice&is_workday',
    'dishash&slice&wea',
#    'dishash&slice&temp',
#    'dishash&slice&pm25',
#
#    'dishash&slice&tf1',
#    'dishash&slice&tf2',
#    'dishash&slice&tf3',
#    'dishash&slice&tf4',
#




    'dishash&dayofweek',
    'dishash&is_workday',
    'dishash&wea',
    'dishash&temp',
    'dishash&pm25',

    'dishash&tf1',
    'dishash&tf2',
    'dishash&tf3',
    'dishash&tf4',


    'slice&dayofweek',
    'slice&is_workday',
    'slice&wea',
    'slice&temp',
    'slice&pm25',

    'slice&tf1',
    'slice&tf2',
    'slice&tf3',
    'slice&tf4',


]
