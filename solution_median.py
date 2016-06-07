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










def build_median_map(file):
    avg_map = {}
    with open(file,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem,gap = ws[0],ws[1],ws[2]
            dis , dayslice = ws[3].split('-',1)
            slice = dayslice.split('-')[-1]

            key = dis+'-'+slice

            if key not in avg_map:
                avg_map[key] = []
            avg_map[key].append(float(gap))
    #median .
    for key in avg_map:
        vec = avg_map[key]
        vec = sorted(vec)
        avg_map[key] = vec[len(vec)/2]
    return avg_map




def update(vecmap, pred_try):
    for k in vecmap:
        v = vecmap[k]
        if distance(v , k ) > distance( pred_try ,  k):
            vecmap[k] = pred_try
def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])


    predfile = config.get('prediction','pred_obj' )
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)


    avgmap = build_median_map(config.get('train','ins_merge_path')  )
    # load_stat_order_avg(config.get('train','stat_order_avg') , avgmap )
    result = []
    for dayslice in predvec:
        for dishash in cluster_map:


            slice =  dayslice.split('-')[-1]
            key = dishash + '-' + slice

    #        print avgmap[key],slice
            avg = avgmap.get(key,-1)
            if float(avg) < 1:
                avg = 1

            node = [cluster_map[dishash] , dayslice, str(avg)]
            result.append(node)

    with open(config.get('bingo','median_bingo'), 'w') as f:
        for node in result:
            f.write(','.join(node)+'\n')

    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()
