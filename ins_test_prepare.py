__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser,logging
from data_transform import *
from data_transform import filter_fea
from data_transform import expand_cross_feature
# fit the liblinear format .
logging.basicConfig(filename="ins.test.log",
                    level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(filename)s[line:%(lineno)d] %(message)s',
                    filemode='a',
                    datefmt='%a, %d %b %Y %H:%M:%S')
from common import *
#watch the dense feas # it's important.

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
    predslice = build_pred_slice(config.get('prediction','pred_obj' ))

    # trend_map = build_trend_map(config.get('train','ins_merge_path'))
    trend_map = read_trend_map(config.get('train','trend_map'))
    sup_map = read_trend_map(config.get('train','sup_map'))
    idmap = build_id_map(insfeamap)

    loss_sum = 0

    f_sup = open(config.get('test','sup_sample') , 'w')

    f_dem = open(config.get('test','dem_sample'), 'w')
    f_gap = open(config.get('test','gap_sample') ,'w')

    with open(insmergefile,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem ,gap ,inskey = ws[0],ws[1],ws[2],ws[3]
            if inskey.split('-')[-1] not in predslice:
                continue
            vec=[]

            dishash = inskey.split('-')[0]

            ws.append('dishash='+dishash)
            # curid ,disfea = dishash_feature(idmap,dishash,1000000)
            # vec.append(disfea)

            arfs = build_auto_regression_fea(dishash, inskey.split('-',1)[-1]  ,trend_map,sup_map)
            ws.extend(arfs)

            kvmap = {'dishash':dishash}
            for fea in ws[4:]:
                k,v = fea.split('=')
                kvmap[k] = v

            build_continous_fea(kvmap)
            for k in kvmap:
                v = kvmap[k]
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

                vec.append('{id}:{val}'.format(id=id,val=val))
            curid , cfvec = expand_cross_feature(kvmap,idmap,100000)
            vec.extend(cfvec)

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
