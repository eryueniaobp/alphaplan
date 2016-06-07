__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser,logging
from data_transform import  *
from data_transform import distance
from common import *
import numpy as np
# fit the liblinear format .
logging.basicConfig(filename="ins.pred.log",
                    level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(filename)s[line:%(lineno)d] %(message)s',
                    filemode='a',
                    datefmt='%a, %d %b %Y %H:%M:%S')

#watch the dense feas # it's important.





def calc_mape(num,vec):
    if num == 0:
        return 1e10
    sum = 0
    for i in vec:
        if i == 0 :
            continue
        sum += abs( (num-i)/i)
    return sum
def minimize_mape(vec):
    min = 1e9
    pivot = 0
    for i in vec:
        mape = calc_mape(i,vec)
        if mape < min :
            min , pivot = mape , i
    return min ,pivot



def build_avg_map(file):
    avg_map = {}
    var_map = {} #variance
    with open(file,'r') as f:
        for L in f:
            ws = L.strip().split(',')
            sup,dem,gap = ws[0],ws[1],ws[2]
            dis , dayslice = ws[3].split('-',1)
            slice = dayslice.split('-')[-1]
            #exclude the outlier.
            if dayslice[0:10] == '2016-01-01':
                continue
            key = dis+'-'+slice

            if key not in avg_map:
                avg_map[key] = []
            avg_map[key].append(float(gap))
    #.avg
    for key in avg_map:
        vec = avg_map[key]
        minmape,pivot = minimize_mape(vec)
        if pivot ==0:
            print key ,vec
        if np.mean(vec) > 10* pivot:
            print vec,np.mean(vec),pivot
        var_map[key] = (np.mean(vec),np.median(vec),np.var(vec), pivot)

        gap_sum = sum(vec)
        avg_map[key] = gap_sum/len(vec)
        
    return var_map ,avg_map

def save_stat_map(file,map,val_index , cluster_map):
    slices= [ str(i+1) for i in range(144) ]
    head = ['']

    with open(file,'w') as f:
        for dishash in cluster_map:
            head.append( dishash+':'+cluster_map[dishash])
        f.write(  ','.join(head) + '\n')

        for slice in slices:
            vec = [slice]
            for dishash in cluster_map:
                key = dishash+'-'+slice
                if key in map:
                    val = map[key][val_index]
                else:
                    val = -1
                vec.append(val)
            vec = [str(i) for i in vec]
            f.write( ','.join(vec) + '\n')




def update(vecmap, pred_try):
    for k in vecmap:
        v = vecmap[k]
        if distance(v , k ) > distance( pred_try ,  k):
            vecmap[k] = pred_try
def predict(predvec, cluster_map , file, statmap , val_index ):
    result = []
    for dayslice in predvec:
        for dishash in cluster_map:


            slice =  dayslice.split('-')[-1]
            key = dishash + '-' + slice
    #        print avgmap[key],slice
            avg = statmap[key][val_index]
            if avg == 0 : 
                print 'miss , ' , key
            if float(avg) < 1:
                avg = 1
            node = [cluster_map[dishash] , dayslice, str(avg)]
            result.append(node)

    with open(file, 'w') as f:
        for node in result:
            f.write(','.join(node)+'\n')
def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    predfile = config.get('prediction','pred_obj' )
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)


    statmap , avgmap = build_avg_map(config.get('train','ins_merge_path')   )

    predict(predvec,cluster_map,config.get('bingo','avg_bingo') ,statmap, 0 )
    predict(predvec,cluster_map,config.get('bingo','median_bingo') ,statmap, 1 )
    predict(predvec,cluster_map,config.get('bingo','mape_bingo') ,statmap, 3 )


    save_stat_map(config.get('train','avg_map') , statmap, 0 ,  cluster_map)
    save_stat_map(config.get('train','mape_map') , statmap,  3, cluster_map)
    save_stat_map(config.get('train','var_map') , statmap, 2 , cluster_map)

    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()
