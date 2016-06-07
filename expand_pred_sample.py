__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser,logging
from data_transform import  *
from data_transform import distance
from common import *
# fit the liblinear format .
logging.basicConfig(filename="ins.pred.log",
                    level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(filename)s[line:%(lineno)d] %(message)s',
                    filemode='a',
                    datefmt='%a, %d %b %Y %H:%M:%S')

#watch the dense feas # it's important.


def build_id_map(mapfile):
    idmap = {}
    with open(mapfile , 'r') as f:
        for L in f:
            key , id   = re.split('\s+',L.strip())
            idmap[key] = id
    return idmap



def iter_idfea(kvmap,idmap):
    loss_sum = 0
    for k in kvmap:
        v =  kvmap[k]
        if filter_fea(k,v):
            continue
        if k in sparse_feas:
            idkey  = '{k}={v}'.format(k=k,v=v)
        else:
            idkey = k
        if idkey not in idmap:
            loss_sum +=1
            logging.warn(idkey + ' not in the id map')
            continue
        id = idmap[idkey]
        if k in sparse_feas:
            val = 1
        else:
            val = v

        yield '{id}:{val}'.format(id=id,val= val )
    curid , cfvec = expand_cross_feature(kvmap , idmap , 1000000)
    for idval in cfvec:
        yield idval


def expand(dayslice , dishash ,weather_data ,poi_data , trf_data , idmap , f ,fraw, trend_map,sup_map):
    weather_key = dayslice
    traffic_key = dishash + '-' + dayslice
    poi_key = dishash

    weather_feas = get_weather_feas(weather_key,weather_data)
    trf_feas = get_traffic_feas(traffic_key , trf_data)
    poi_feas = get_poi_feas(poi_key , poi_data)

    sparse_feas = [
        'dishash={dis}'.format(dis=dishash),
        'dayofweek={d}'.format(d= parse_dayofweek(dayslice[0:10]) )   ,
                   'is_workday={iw}'.format(iw= is_workday(dayslice[0:10]) ),
                   'slice={s}'.format(s=dayslice[11:])
                    ]
    feas = []
    feas.extend(sparse_feas)
    feas.extend(poi_feas)
    feas.extend(trf_feas)
    feas.extend(weather_feas)


    arfs = build_auto_regression_fea(dishash, dayslice  ,trend_map,sup_map,trf_data,weather_data)

    feas.extend(arfs)


    raw=['0']
    raw.extend(feas)
    fraw.write('\t'.join(raw) + '\n')


    kvmap = {}
    for fea in feas:
        k,v = fea.split('=')
        kvmap[k] = v
    build_continous_fea(kvmap)
    vec = ['0']
    for fea in iter_idfea(kvmap,idmap):
        vec.append(fea)
    f.write('\t'.join(vec) + '\n')










def update(vecmap, pred_try):
    for k in vecmap:
        v = vecmap[k]
        if distance(v , k ) > distance( pred_try ,  k):
            vecmap[k] = pred_try
def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])
    insfile = config.get('test','ins_path')
    insmergefile= config.get('test','ins_merge_path')
    insfeamap = config.get('feamap','fea_map_path')  #out

    predfile = config.get('prediction','pred_obj' )
    predins = config.get('prediction','pred_ins')
    # pred_binary_ins=./test_sample/predins.binary
    # predins_bin = config.get('prediction','pred_binary_ins')

    predinsraw = config.get('prediction','pred_ins_raw')
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)
    idmap = build_id_map(insfeamap)

    weather_data = {}
    load_weather(config.get('test','weather_data') ,weather_data)
    poi_data = {}
    load_poi(config.get('test','poi_data'),poi_data)
    trf_data = {}
    load_traffic(config.get('test' , 'traffic_data') , trf_data)


    # sup_map , trend_map = build_trend_map(config.get('train','ins_merge_path'))
    trend_map = read_trend_map(config.get('train','trend_map'))
    sup_map = read_trend_map(config.get('train','sup_map'))

    result = []

    # f_bin = open(predins_bin,'w')

    with open(predinsraw,'w') as fraw:
        with open(predins,'w') as f:
            for dayslice in predvec:
                for dishash in cluster_map:
                    expand(dayslice , dishash ,weather_data ,poi_data , trf_data , idmap , f ,fraw, f_bin, trend_map,sup_map)

                    node = [cluster_map[dishash] , dayslice, '0']
                    result.append(node)
    # f_bin.close()
    with open(config.get('prediction','result'), 'w') as f:
        for node in result:
            f.write(','.join(node)+'\n')




    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()
