__author__ = 'baidu'


from sklearn import linear_model
import numpy as np
import ConfigParser,sys ,re
from solution_trend import  *
def cal_mape(ty):
    mape = 0 
    cnt = 0
    for i in ty:
        if i[0] > 0 :
            cnt+=1
            mape += abs( i[1] - i[0]) /i[0] 
    return mape,cnt 

def gap_status(ds,trend_map):
    vec = []
    #20 ,51
    spedis = ['91690261186ae5bee8f83808ea1e4a01','d4ec2125aff74eded207d2d915ef682f']
    for sd in spedis:
        spe = trend_map[sd].get(ds,1)
        total = max(1, trend_map['TOTAL'].get(ds,1))
        spe_ratio = spe/total
        vec.extend([spe,total,spe_ratio])
    return vec
def get_val(trend_map , dishash,ds):
    if ds in trend_map[dishash]:
        return trend_map[dishash][ds] 
    else:
        #avg 
        days = ['2016-01-{day}'.format(day=str(day+1).zfill(2)) for day in range(1,21) ] 
        dayslice = [] 
        slice = ds.split('-')[-1]
        for d in days:
            dayslice.append(d+'-'+slice)
        vec = []
        for ds in dayslice:
            vec.append(trend_map[dishash].get(ds,1))
#        print 'miss',dishash,ds, vec
        return np.mean( vec ) 
def build_linear_XY(dishash,slice,trend_map):
    days = ['2016-01-{day}'.format(day=str(day+1).zfill(2)) for day in range(1,21) ]
    dayslice = []
    for d in days:
        dayslice.append(d+'-'+slice)
    X = []
    Y = []
    for ds in dayslice:
        y = get_val(trend_map,dishash,ds)
        Y.append(y)


        vec = []
        for pds in iter_prev_dayslice(ds, 3):
            vec.append(get_val(trend_map,dishash,pds))
            vec.extend(gap_status(pds,trend_map))
        iw = is_workday2(ds[0:10])
        vec.append(iw)
        X.append(vec)

    return X , Y


def build_pred_X(dishash,ds,trend_map):
    vec = []
    for pds in iter_prev_dayslice(ds, 3):
        vec.append(get_val(trend_map,dishash,pds))
        vec.extend(gap_status(pds,trend_map))
    iw = is_workday2(ds[0:10])
    vec.append(iw)
    return vec


def linear_reg():

    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    predfile = config.get('prediction','pred_obj' )
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)

    trend_map = read_trend_map(config.get('train','trend_map'))
    # sup_map,trend_map = build_trend_map(config.get('train','ins_merge_path')   )

    file = config.get('bingo','linear_reg_bingo')

    predslice = build_pred_slice(predfile)


    mape = 0 
    clfmap = {}
    ty = [] 
    for dishash in cluster_map:
        for slice in predslice:
            clf = linear_model.LinearRegression()
            X , y = build_linear_XY(dishash,slice,trend_map )
            clf.fit(X,y)
            py = clf.predict(X) 
            py = [ max(i,1) for i in py ] 
            for node in zip(zip(y,py),X):
                print node
            ty.extend(zip(y,py))
            mape,cnt = cal_mape(zip(y,py))
            
            print dishash+':'+str(cluster_map[dishash]) ,slice,' mape= ' , mape/max(cnt,1) , ' cnt=' , cnt  
            print dishash+':'+str(cluster_map[dishash]) ,slice , clf.coef_,clf.intercept_
            key = dishash +'-' +str( slice )
            clfmap[key] = clf
    mape,cnt =cal_mape(ty)
    print 'mape= ' , mape/max(cnt,1) , ' cnt=' , cnt  
    with open(file,'w') as f:
        for dishash in cluster_map:
            for ds in predvec:
                #
                clf = clfmap[dishash+'-'+ ds.split('-')[-1]]

                vec = build_pred_X(dishash,ds,trend_map)
                val = max(1,clf.predict([vec])[0])
                slice =ds.split('-')[-1] 
                if cluster_map[dishash] == '28' and slice == '130':
                    print dishash+':'+str(cluster_map[dishash]),ds, np.array(vec)*np.array(clf.coef_), clf.intercept_  ,val 
                f.write('{id},{ds},{gap}\n'.format(id=cluster_map[dishash] ,
                                                   ds = ds  ,gap = val ))

if __name__ == '__main__':
    linear_reg()

