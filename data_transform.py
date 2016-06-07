__author__ = 'baidu'

import ConfigParser ,re,sys ,datetime,random,logging
from common import *
logging.basicConfig(filename="alpha.log",
                    level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(filename)s[line:%(lineno)d] %(message)s',
                    filemode='a',
                    datefmt='%a, %d %b %Y %H:%M:%S')
def read_trend_map(file):
    trend_map = {}
    with open(file,'r') as f:
        head = []

        for L in f:
            ws = L.strip().split(',')
            if ws[0] == '':
                dis = [ k.split(':')[0] for k in ws[1:] ]
                head.extend(dis)
                for x in head:
                    trend_map[x] = {}
            else:
                for i in range(len(head)):
                    x = head[i]
                    dayslice = ws[0]

                    trend_map[x][dayslice] = float(ws[1+i])

    return trend_map





def build_trend_map(file):
    trend_map = {}
    sup_map = {}
    with open(file,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem,gap = ws[0],ws[1],ws[2]
            dis , dayslice = ws[3].split('-',1)
            slice = dayslice.split('-')[-1]
            #exclude the outlier.
            if dayslice[0:10] == '2016-01-01':
                continue
            # key = dis+'-'+slice
            if dis not in trend_map:
                trend_map[dis] = {}
            if dis not in sup_map:
                sup_map[dis] = {}
            trend_map[dis][dayslice] = float(gap)
            sup_map[dis][dayslice] = float(sup)


    return sup_map , trend_map

def poi_distance(poimap , src,dst):
    if src not in poimap or dst not in poimap:
        logging.warn(src + ' or ' + dst + ' not in the poimap')
    dist = 0
    for src_key in poimap[src]:
        src_num = poimap[src].get(src_key, 0)
        dst_num = poimap[dst].get(src_key, 0)
        dist += abs(src_num - dst_num)

    return abs(dist)
def find_nearest_district(poimap , dishash):
    min_dis = 1e10
    thash = 0
    for key in poimap:
        if key == dishash:
            continue
        dis = poi_distance(poimap,dishash,key)
        print key, dis
        if dis < min_dis:
            min_dis = dis
            thash = key

    return min_dis, thash
def build_cluster_map(clustermapfile):
    cluster_map = {}
    with open(clustermapfile,'r') as f:
        for L in f:
            dishash , id = re.split('\s+',L.strip())
            cluster_map[dishash] = id
    return cluster_map
def expand_cross_feature(kvmap,idmap,curid):
    vec = []
    for cf in cross_feas:
        ks = cf.split('&')
        try:
            vs = [ str(transform_value(k,kvmap[k])) for k in ks ]
        except:
            continue

        fea = '{key}={val}'.format(
            key = cf ,
            val = '&'.join(vs)
        )
        idkey =fea


        if idkey not in idmap:
            idmap[idkey] = curid
            curid +=1

        vec.append('{id}:{val}'.format(
            id = idmap[idkey] ,
            val = 1 ,
        ))
    return curid , vec




def dishash_feature(idmap ,dishash,curid):
    key = 'dishash=' + dishash
    if key in idmap:
        return curid ,  '{id}:{val}'.format(id=idmap[key],val = 1 )
    else:
        idmap[key] = curid
        return curid+1 , '{id}:{val}'.format(id=idmap[key] ,val =1 )
def distance( k1 , k2 ) :
    if k1 == 'NEVER':
        return 1e10
    s1 = k1.split('-')[3]
    s2 = k2.split('-')[3]
    s1 = slice_to_hour(s1)
    s2 = slice_to_hour(s2)
    t1 = datetime.datetime.strptime(k1[0:10] + '-'  + s1 , '%Y-%m-%d-%H:%M')
    t2 = datetime.datetime.strptime(k2[0:10] + '-' + s2 , '%Y-%m-%d-%H:%M' )

    return abs((t1-t2).total_seconds())



def is_workday(day):
    if  datetime.datetime.strptime(day, '%Y-%m-%d').weekday() >= 5:
        return False
    if day == '2016-01-01':
        return False #new year holiday
    return True
def build_pred_slice(predfile):
    predvec = build_pred_obj(predfile)
    slices = set()
    for i in predvec:
        slices.add(i.split('-')[-1])
    return slices
def build_pred_obj(predfile):
    vec = []
    with open(predfile,'r') as f:
        for L in f:
            if '2016' in L:
                vec.append(L.strip())
    return vec
def build_ins_key(dishash, day,hour):
    return '{dist}-{day}-{slice}'.format(dist=dishash,day=day,slice=parse_time_slice(hour))

def build_traffic_key(dishash,day,hour):
    return '{dist}-{day}-{slice}'.format(dist=dishash,day=day,slice=parse_time_slice(hour))

def build_weather_key(day,hour):
    return '{day}-{slice}'.format(day=day,slice = parse_time_slice(hour))

def smooth_traffic_data(traffic_data):
    for key in traffic_data:

        traffic_data[key]['tf1'] = traffic_data[key]['tf1'] / (traffic_data[key]['cnt'] + 0.)
        traffic_data[key]['tf2'] = traffic_data[key]['tf2'] / (traffic_data[key]['cnt'] + 0.)
        traffic_data[key]['tf3'] = traffic_data[key]['tf3'] / (traffic_data[key]['cnt'] + 0.)
        traffic_data[key]['tf4'] = traffic_data[key]['tf4'] / (traffic_data[key]['cnt'] + 0.)
        if traffic_data[key]['cnt'] > 1:
            logging.info('hit smooth , key = ' + key )

def append_dict_value( map , key , num):
    num = int(num)
    if key in map:
        map[key] += num
    else:
        map[key] = num

def iter_poi_cate(cates):
    cs= cates.split('#')


    key = ''
    for c in cs:
        key += c
        yield '{key}'.format(key=key)
        key += '#'

def get_poi_feas(dishash ,poi_data):
    if dishash not in poi_data:
        logging.warn(dishash + ' is not in the poi_data')
        # raise KeyError('The key is not in the poi_data')
        return []
    poi_feas =  []
    for k in poi_data[dishash]:
        v = poi_data[dishash][k]
        poi_feas.append( '{k}={v}'.format(
            k=k ,
            v=v ,
        ))
    return poi_feas


def date2key(day):
    return day.strftime('%Y-%m-%d') + '-' + str(parse_time_slice(day.strftime('%H:%M:%S')))









def load_poi(poi_file,poi_data):
    logging.info('load_poi ' + poi_file)
    print 'load_poi', poi_file

    with open(poi_file,'r') as f:
        for L in f:
            ws = re.split('\s+',L.strip())
            dishash = ws[0]
            poi_data[dishash] = {}
             # 20#7:249
            for poi in ws[1:]:
                try:
                    cate , num = poi.strip().split(':',1)

                except:
                    print >>sys.stderr, 'poi error ' ,  poi
                    continue
                for key in iter_poi_cate(cate):
                    append_dict_value(poi_data[dishash] , key , num)


def load_traffic(file,traffic_data):
    logging.info(file)
    # 1ecbb52d73c522f184a6fc53128b1ea1        1:231   2:33    3:13    4:10    2016-01-01 23:30:22
    with open(file, 'r') as f:
        for L in f:
            dishash ,tf1,tf2,tf3,tf4 , day ,hour  = re.split('\s+',L.strip())
            key  = build_traffic_key(dishash,day,hour)
            if key in traffic_data:
                traffic_data[key]['cnt'] +=1
                traffic_data[key]['tf1'] += int(tf1[2:])
                traffic_data[key]['tf2'] += int(tf2[2:])
                traffic_data[key]['tf3'] += int(tf3[2:])
                traffic_data[key]['tf4'] += int(tf4[2:])
            else:
                traffic_data[key] = {}
                traffic_data[key]['cnt'] = 1
                traffic_data[key]['tf1'] = int(tf1[2:])
                traffic_data[key]['tf2'] = int(tf2[2:])
                traffic_data[key]['tf3'] = int(tf3[2:])
                traffic_data[key]['tf4'] = int(tf4[2:])
def load_weather(file,weather_data):
    logging.info(file)
    with open(file,'r') as f:
        for L in f:
            day ,hour , int_wea ,double_temp ,double_pm25  = re.split('\s+',L.strip())
            wea = int(int_wea)
            temp = float(double_temp)
            pm25 = float(double_pm25)
            key  = build_weather_key(day,hour)
            # if key in weather_data:
            #     raise ValueError('repeated weather data')

            # Will use the last weather data.
            weather_data[key] = {'wea': wea , 'temp':temp , 'pm25':pm25}
def save_district_slice_map(file, map):
    logging.info('save district slice map')
    with open(file,'w') as f:
        for key in map:
            f.write('{key},{day},{cnt},{dem},{sup},{gap}\n'.format(
                key=key,
                day=len(map[key]['day']),
                cnt=map[key]['cnt'],
                dem=map[key]['dem'],
                sup=map[key]['sup'],
                gap=(map[key]['dem'] - map[key]['sup'])/len(map[key]['day'])
            ))
def load_stat_order_avg(file,map):
    with open(file,'r') as f:
        for L in f:
            ws  = L.strip().split(',')
            dishash,slice  =ws[0].split('-')
            if dishash not in map:
                map[dishash] = {}
            map[dishash][slice] = ws[-1]
def update_district_slice_map(map,dishash,day,slice, sup,dem):
    key  = dishash+'-'+str(slice)
    if key not in map:
        days = set()
        days.add(day)
        map[key] = {
            'day': days,
            'cnt': 1,
            'sup': float(sup),
            'dem': float(dem),
        }
    else:
        map[key]['day'].add(day) 
        map[key]['cnt']+=1
        map[key]['sup']+=float(sup)
        map[key]['dem']+=float(dem)
#Need to yield instance .
def load_order(file,poi_data,traffic_data,weather_data):
    print str(len(poi_data)) , str(len(traffic_data ) ), str(len(weather_data) )
    logging.info(file  + ' ' + str(len(poi_data)) + ' ' + str(len(traffic_data ) ) + ' ' + str(len(weather_data)))
#order data print . key point .
    suffix = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '-' + str(random.randint(0,1e4))
    gap_file = config.get(phase,'sample_path') + '/gap.' + suffix
    dem_file = config.get(phase,'sample_path') + '/dem.' + suffix
    sup_file = config.get(phase,'sample_path') + '/sup.' + suffix

    ins_file = config.get(phase,'sample_path') + '/ins.' + suffix

    fw_gap = open(gap_file,'w')
    fw_dem = open(dem_file,'w')
    fw_sup = open(sup_file,'w')
    fw_ins = open(ins_file,'w')

    district_slice_map = {}
    # todo : sliding average  sup,dem,gap
    #  can do it when merge the instance.
    # time :  holiday  . 1.1 -1.3. New Year holiday . But thereis no more holiday in Januray. So Mayby it 's not important.
    ln = 0 
    with open(file,'r') as f:
        for L in f:
            try:
                order_id, driver_id , passenger_id, start_district_hash,dest_district_hash ,price ,day,hour  = re.split('\s+',L.strip())
                if driver_id == 'NULL':
                    sup ,dem ,gap = 0 , 1, 1
                else:
                    sup ,dem ,gap  = 1,1 , 0
                slice =  parse_time_slice(hour)
                dayofweek = parse_dayofweek(day)
                b_workday = is_workday(day)
                update_district_slice_map(district_slice_map,start_district_hash,day,slice,sup,dem)
                ln+=1 
                if ln%100000 == 0:
                    logging.info('order '+str(ln))
                # continue
                #todo: the relationship between district.
                #ins_key : dishash+dayofweek+slice ?
                ins_key  = build_ins_key(start_district_hash , day,hour )

                poi_feas = get_poi_feas(start_district_hash,poi_data)
                traffic_feas = get_traffic_feas(build_traffic_key(start_district_hash,day,hour), traffic_data)
                weather_feas =get_weather_feas(build_weather_key(day,hour), weather_data)

                insvec = [str(sup),str(dem),str(gap)]
                insvec.append(ins_key)
                insvec.append('dayofweek='+str(dayofweek))
                insvec.append('is_workday='+str(b_workday))
                insvec.append('slice='+str(slice))
                insvec.extend(poi_feas)
                insvec.extend(traffic_feas)
                insvec.extend(weather_feas)

                line = ','.join(insvec)

                fw_ins.write(line + '\n')



                #  sup ,dem ,gap ,   ins_key , dayofweek , slice , poi-map , traffic-map,weather-map
            except Exception as e:
                print >>sys.stderr,e


    fw_gap.close()
    fw_dem.close()
    fw_sup.close()
    fw_ins.close()

    save_district_slice_map(config.get(phase,'stat_order_avg') , district_slice_map)
def load_cluster_map(file,cluster_map):
    with open(file,'r') as f:
        for L in f:
            dishash , id = re.split('\s+',L.strip())
            cluster_map[dishash] = id

def main():

    cluster_map = {}
    load_cluster_map(config.get(phase, 'cluster_map'),cluster_map)

    poi_data = {}
    load_poi(config.get(phase,'poi_data'),poi_data)

    traffic_data = {}
    load_traffic(config.get(phase , 'traffic_data') , traffic_data)
    smooth_traffic_data(traffic_data) #average

    weather_data =  {}
    load_weather(config.get(phase, 'weather_data') , weather_data)

    load_order(config.get(phase,'order_data'),poi_data,traffic_data,weather_data)

    # for ins in load_order(config.get(phase,'order_data'),poi_data,traffic_data,weather_data) :
    #     pass

    logging.info('done')
trf_miss_key  =set()
if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])
    phase = sys.argv[2]

    main()

