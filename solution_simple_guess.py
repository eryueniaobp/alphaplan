__author__ = 'baidu'
import  numpy as np
from data_transform import *
from common import *
# p=pmax(1,(p1*0.65+p2*0.25+p3*0.15)/2)

def guess():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    predfile = config.get('prediction','pred_obj' )
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)
    cluster_map =  build_cluster_map(clustermapfile)

    trend_map = read_trend_map(config.get('train','trend_map'))

    bingo_guess = config.get('bingo','guess_bingo')
    with open(bingo_guess ,'w') as f:
        for dishash in cluster_map:
            for ds in predvec:
                vec = []
                for pds in iter_prev_dayslice(ds, 3):
                    vec.append(trend_map[dishash].get(pds,1))
                val = max( 1,  sum( np.array(vec) * np.array([0.65,0.25,0.15])  ) /2 )
                f.write('{disid},{ds},{val}\n'.format(
                    disid = cluster_map[dishash] ,
                    ds = ds ,
                    val = val

                ))


if __name__ == '__main__':
    guess()
