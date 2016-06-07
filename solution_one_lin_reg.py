__author__ = 'baidu'


from sklearn import linear_model
import numpy as np
import ConfigParser,sys ,re
from solution_trend import  *
from solution_linear_regression import *



def one_linear_reg():

    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    predfile = config.get('prediction','pred_obj' )
    clustermapfile = config.get('prediction','cluster_map')


    predvec = build_pred_obj(predfile)

    cluster_map =  build_cluster_map(clustermapfile)


    # trend_map = build_trend_map(config.get('train','ins_merge_path')   )
    trend_map = read_trend_map(config.get('train','trend_map'))

    file = config.get('bingo','linear_reg_bingo')

    predslice = build_pred_slice(predfile)

    # clfmap = {}
    clf = linear_model.LinearRegression()
    TX = []
    TY = []
    for dishash in cluster_map:
        for slice in predslice:

            X , y = build_linear_XY(dishash,slice,trend_map )
            TX.extend(X)
            TY.extend(y)

    clf.fit(TX,TY)

    py = clf.predict(TX)
    ty = zip(TY,py)
    mape,cnt =cal_mape(ty)
    print 'mape= ' , mape/max(cnt,1) , ' cnt=' , cnt

    with open(file,'w') as f:
        for dishash in cluster_map:
            for ds in predvec:
                #
                # clf = clfmap[dishash+'-'+ ds.split('-')[-1]]

                vec = build_pred_X(dishash,ds,trend_map)

                val = max(1,clf.predict([vec])[0])
                f.write('{id},{ds},{gap}\n'.format(id=cluster_map[dishash] ,
                                                   ds = ds  ,gap = val ))
    print clf.coef_,clf.intercept_
if __name__ == '__main__':
    one_linear_reg()

