__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser,logging
from data_transform import  *
from data_transform import distance
from common import *
# fit the liblinear format .
logging.basicConfig(filename="ins.test.log",
                    level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(filename)s[line:%(lineno)d] %(message)s',
                    filemode='a',
                    datefmt='%a, %d %b %Y %H:%M:%S')



def build_id_map(mapfile):
    idmap = {}
    with open(mapfile , 'r') as f:
        for L in f:
            key , id   = re.split('\s+',L.strip())
            idmap[key] = id
    return idmap





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
    clustermapfile = config.get('prediction','cluster_map')

    idmap = build_id_map(insfeamap)
    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)

    loss_sum = 0

    vecmap = {

    }
    for k in predvec:
        vecmap[k] = 'NEVER'

    with open(insmergefile,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem ,gap ,inskey = ws[0],ws[1],ws[2],ws[3]

            pred_try = inskey.split('-',1)[1]
            update(vecmap,pred_try)

    with open(config.get('prediction','pred_pretty_obj'),'w') as f:
        for k in vecmap:
            print k,vecmap[k]
            f.write(vecmap[k] + '\n')




    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()