__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser,logging
from common import *
from data_transform import *
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


def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])
    insfile = config.get('test','ins_path')
    insmergefile= config.get('test','ins_merge_path')
    insfeamap = config.get('feamap','fea_map_path')  #out

    predfile = config.get('prediction','pred_pretty_obj' )
    clustermapfile = config.get('prediction','cluster_map')

    idmap = build_id_map(insfeamap)
    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)

    loss_sum = 0

    f_sup = open(insmergefile +'.sup.pred' , 'w')
    f_dem = open(insmergefile + '.dem.pred', 'w')
    f_gap = open(insmergefile +'.gap.pred','w')
    with open(insmergefile,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem ,gap ,inskey = ws[0],ws[1],ws[2],ws[3]

            pred_try = inskey.split('-',1)[1]
            if pred_try not in predvec:
                continue
            vec=[]
            for fea in ws[4:]:
                k,v = fea.split('=')

                if k in sparse_feas:
                    idkey  = fea

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

                vec.append('{id}:{val}'.format(id=id,val=val))

            f_sup.write(sup+'\t'+ '\t'.join(vec)+'\n')
            f_dem.write(dem+'\t'+'\t'.join(vec)+'\n')
            f_gap.write(gap+'\t'+'\t'.join(vec)+'\n')



    f_sup.close()
    f_dem.close()
    f_gap.close()



    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()