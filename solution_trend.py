__author__ = 'baidu'


from data_transform import  *
from common import *
import numpy as np
import  copy

def check_trend_map(trend_map,  cluster_map , predvec):
    days = [ '2016-01-{i}'.format( i = str(i+1).zfill(2))  for i in range(1,21)]
    slices = set()
    for ds in predvec:
        slices.add(ds.split('-')[-1])
    for dishash in cluster_map:

        for slice in slices:
            for day in days:
                ds = day+'-'+slice
                val = max( trend_map[dishash].get(ds,1) ,1 )

                r = iter_prev_dayslice(ds, 1).next()
                pval = max(trend_map[dishash].get(r,1),1)

                if val > 10* pval:
                    print dishash , ds , pval , val


def trend_val(vec):
    return max(vec[0],1) 
def save_trend_bingo(file,trend_map, cluster_map,predvec ):
    with open(file,'w') as f:
        for dishash in cluster_map:
            for ds in predvec:
                vec = []
                for pds in iter_prev_dayslice(ds, 3):
                    try:
                        vec.append(trend_map[dishash][pds])
                    except Exception as e:
                        print 'trend-exp:' , dishash,pds , e
                        vec.append(1)
                val = trend_val(vec)
                f.write('{id},{ds},{gap}\n'.format(id=cluster_map[dishash] ,
                                                   ds = ds  ,gap = val ))
def avg_consume(trend_map,dishash,ds):
    days = ['2016-01-{day}'.format(day=str(day+1).zfill(2)) for day in range(21) ]
    vec = []
    for day in days:
        curds = day +'-'  +ds.split('-')[-1]
        prevds = iter_prev_dayslice(curds , 1).next()

        prev_val = trend_map[dishash].get(prevds,1.0)

        cur_val = trend_map[dishash].get(curds,1.0)

        vec.append(max(prev_val - cur_val , 0))
    return np.mean(vec)
def save_consume_map(file,map,cluster_map):
    with open(file,'w') as f:
        for key in map:
            dishash , ds  = key.split('-',1 )
            # for dishash in cluster_map:
            f.write('{disid},{ds},{consume}\n'.format(disid=cluster_map[dishash],
            ds = ds , consume=map[key]))

def build_history_consume_map(trend_map,cluster_map,predvec):
    consume_map = {}
    for dishash in cluster_map:
        for ds in predvec:
            key = dishash +'-'+ds
            val = avg_consume(trend_map,dishash,ds)
            consume_map[key] = val
    return consume_map

def trend_val_with_consume_map(vec, history_consume_map,dishash,ds):
    key = dishash+'-'+ds
    consume = max( history_consume_map.get(key,0) ,0)
    return max( vec[0] - consume   ,1)
def save_smart_trend_bingo(file,trend_map,cluster_map,predvec,history_consume_map):
    with open(file,'w') as f:
        for dishash in cluster_map:
            for ds in predvec:
                vec = []
                for pds in iter_prev_dayslice(ds, 3):
                    try:
                        vec.append(trend_map[dishash][pds])
                    except Exception as e:
                        print 'trend-exp:' , dishash,pds , e
                        vec.append(1)
                val = trend_val_with_consume_map(vec,history_consume_map,dishash,ds)
                f.write('{id},{ds},{gap}\n'.format(id=cluster_map[dishash] ,
                                                   ds = ds  ,gap = val ))

#KEEP: don't change the function.
def save_trend_map(file,trend_map, cluster_map,predvec ):
    days = ['2016-01-{day}'.format(day=str(day+1).zfill(2)) for day in range(30) ]
    dayslice = []
    for d in days:
        dayslice.extend([ d+'-'+str(slice+1) for slice in range(144) ])
    cluster_map = copy.copy(cluster_map)
    cluster_map['TOTAL'] = '-100'
    trend_map['TOTAL'] = {}
    for ds in dayslice:
        gap_sum = 0
        for dishash in cluster_map:
            if dishash != 'TOTAL':
                gap_sum += trend_map[dishash].get(ds,0)

        trend_map['TOTAL'][ds] = max(gap_sum,0)

    with open(file,'w') as f:
        head = ['']
        for dishash in cluster_map:
            head.append( dishash+':'+cluster_map[dishash])
        f.write(  ','.join(head) + '\n')
        for ds in dayslice:
            vec = [ds]
            for dishash in cluster_map:
                if dishash in trend_map:
                    if ds in trend_map[dishash]:
                        if ds in predvec:
                            print 'conflict'
                        vec.append(trend_map[dishash][ds])
                    else:
                        if ds in predvec:
                            vec.append(-20)
                        else:
                            vec.append(-1)
            vec = [str(i) for i in vec ]
            f.write(','.join(vec)+'\n')



def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    predfile = config.get('prediction','pred_obj' )
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)


    sup_map , trend_map = build_trend_map(config.get('train','ins_merge_path')   )
    #
    # predict(predvec,cluster_map,config.get('bingo','avg_bingo') ,statmap, 0 )
    # predict(predvec,cluster_map,config.get('bingo','median_bingo') ,statmap, 1 )
    # predict(predvec,cluster_map,config.get('bingo','mape_bingo') ,statmap, 3 )


    save_trend_map(config.get('train','trend_map') , trend_map,   cluster_map,predvec)
    save_trend_map(config.get('train','sup_map'),sup_map,cluster_map,predvec)

    save_trend_bingo(config.get('bingo','trend_bingo'),trend_map,cluster_map,predvec)
    history_consume_map = build_history_consume_map(trend_map,cluster_map,predvec)
    save_consume_map(config.get('train','consume_map'),history_consume_map,cluster_map)
    save_smart_trend_bingo(config.get('bingo','smart_trend_bingo'),trend_map,cluster_map,predvec,history_consume_map)
    check_trend_map(trend_map, cluster_map,predvec)
    logging.info( 'done' )
if __name__ == '__main__':
    main()
