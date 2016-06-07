__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser
from data_transform import *
from data_transform import expand_cross_feature
# fit the liblinear format .

from common import  *
def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])
    insfile = config.get('train','ins_path')
    insmergefile= config.get('train','ins_merge_path')
    predslice = build_pred_slice(config.get('prediction','pred_obj' ))

    # trend_map = build_trend_map(config.get('train','ins_merge_path'))
    traffic_data = {}
    traffic_data = {}
    load_traffic(config.get('train' , 'traffic_data') , traffic_data)
    smooth_traffic_data(traffic_data) #average


    weather_data =  {}
    load_weather(config.get('train', 'weather_data') , weather_data)

    trend_map = read_trend_map(config.get('train','trend_map'))
    sup_map = read_trend_map(config.get('train','sup_map'))

    idmap = {}
    curid = 1

    f_sup = open( config.get('train','sup_sample') , 'w')

    f_dem = open( config.get('train','dem_sample'), 'w')
    f_gap = open(config.get('train','gap_sample') ,'w')
#     gap_binary_sample=./train_sample/ins.merge.gap.binary
# gap_divide_val=10

    f_bin_gap = open(config.get('train','gap_binary_sample') , 'w')
    gap_divide_val = float(config.get('train','gap_divide_val'))
    with open(insmergefile,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem ,gap ,inskey = ws[0],ws[1],ws[2],ws[3]
            if inskey.split('-')[-1] not in predslice:
                continue
            vec=[]
            dishash= inskey.split('-')[0]
            ws.append('dishash='+dishash)
            # curid  , disfea = dishash_feature(idmap,dishash,curid)
            # vec.append(disfea)

            arfs = build_auto_regression_fea(dishash, inskey.split('-',1)[-1]  ,trend_map,sup_map , traffic_data,weather_data)
            ws.extend(arfs)

            # vec.extend(arfs)
            kvmap = {'dishash' : dishash} #for cross feature.
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
                    idmap[idkey] = curid
                    curid +=1

                id = idmap[idkey]
                if k in sparse_feas:
                    val = 1
                else:
                    val = v

                vec.append('{id}:{val}'.format(id=id,val=val))
            curid , cfvec = expand_cross_feature(kvmap,idmap,curid)
            vec.extend(cfvec)
            f_sup.write(sup+'\t'+ '\t'.join(vec)+'\n')
            f_dem.write(dem+'\t'+'\t'.join(vec)+'\n')
            f_gap.write(gap+'\t'+'\t'.join(vec)+'\n')

            f_bin_gap.write(binary_gap(gap , gap_divide_val) + '\t'+'\t'.join(vec)+'\n')


    f_sup.close()
    f_dem.close()
    f_gap.close()
    f_bin_gap.close()


    insfeamap = config.get('feamap','fea_map_path')  #out
    with open(insfeamap , 'w') as f:
        for key in idmap:
            f.write('{key}\t{val}\n'.format(key=key ,val = idmap[key]))

    print 'done'

    # idlization ::
if __name__ == '__main__':
    main()