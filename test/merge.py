__author__ = 'baidu'

import re,sys
import numpy as np
import ConfigParser
from operator import itemgetter
#merge the result .
mer_out_conf = [
    [-0.001, 'mer.avg.neg.001.csv'],
    [-0.5 , 'mer.avg.neg.05.csv' ] ,
    [-2 , 'mer.avg.neg.2.csv' ] , # val[1] < val[0]  low the gap of  val[0] ( score0.30 )
    [2,  'mer.avg-2.csv'],  #val[1] > val[0] , low the gap of val[1]
    [5, 'mer.avg-5.csv'] ,
    [10, 'mer.avg-10.csv'] ,
    [20 , 'mer.avg-20.csv'] 
]
#handy sure_map
# 51 2016-01-22-142 11.0 266.045
# 51 2016-01-30-142 10.0 228.6605
# 51 2016-01-28-142 11.0 176.942

# 0122  Friday
# 0128 Thursday
# 0130  Saturday

sure_map = {
    '48,2016-01-22-142': 15 ,
    '42,2016-01-22-142':2 , #33.4364 ,
    '12,2016-01-28-142': 2 , # 23.58732,
    #the folowing 6 points violates the smart-trend .
    '51,2016-01-22-142':10,#266.045,

    '51,2016-01-30-142': 10,#228.6605,
    '51,2016-01-28-142': 10, # 176.942,

    '51,2016-01-26-94': 40 ,
    '51,2016-01-28-94': 40 ,
    '51,2016-01-30-94': 40 ,
    ####################################


    # 23 2016-01-28-142 2.0 25.27585
    '23,2016-01-28-142': 25.27585,
    # 7 2016-01-28-142 1.0 17.8195
    '7,2016-01-28-142': 17.8195  ,

    # 28 2016-01-22-142 1.0 17.42618
    '28,2016-01-22-142': 17.42618 ,

    # 46 2016-01-30-142 1.0 16.1657 special pGap > rGap

    '46,2016-01-30-142': 1.0 ,
    # 22 2016-01-22-142 1.0 17.57155 pGap > rGap
    '22,2016-01-22-142': 2.0 , # 17 is very risky.   the gap will decrease according to the trend_map .
    # 28 2016-01-22-142 1.0 17.42618
    # '28,2016-01-22-142': 17.42618 ,

    # 26 2016-01-24-118 1.0 17.36585  pGap > rGap
    '26,2016-01-24-118': 1.0 , # trend pre 1.0 ; 17 will be very high-risk.

    # 8 2016-01-22-142 1.0 15.70535
    '8,2016-01-22-142': 10 , #  trend prev is 13 ..1 is very high risk.

    # 1 2016-01-28-142 1.0 14.570185
    '1,2016-01-28-142': 14.570185 ,  # pre-trend is 27. it cann't consume so much gap according to the trend-map .


    # 22 2016-01-28-142 1.0 12.27673   pGap >rGap
    '22,2016-01-28-142': 2.0 , #pre-trend is 15 . but it can consume a lot of gaps in history . so be sure <15
# 12 2016-01-26-142 1.0 12.234115
    '12,2016-01-26-142':  12.234115  , #pre -trend is  20 , but low consume-gap-capacity . so 1.0 will high risky!

# 46 2016-01-24-142 1.0 11.63115   pGap > rGap
    '46,2016-01-24-142': 1.0 , #prev-trend is low . low c-gap-cap .  so 11 will be high risky.

    # 12 2016-01-22-142 1.0 11.464545

    '12,2016-01-22-142': 11.464545,  #pre-trend is 15 . low c-gap-cap . so 1.0 will be wrong .

    # 46 2016-01-24-142 1.0 11.63115    pGap >rGap
    '46,2016-01-24-142': 1.0 , #pre-trend is 2.0 ,11 will be very high risky .


    # 26 2016-01-22-94 1.0 12.72835
    '26,2016-01-22-94': 12.72835, # pre-trend is 11 , low c-gap-cap. so 1.0 will be high risk .
}
# sure_map = {}



# handy correct
def make_sure( disid, dayslice ,val ):

    key = disid +',' + dayslice
    if key in sure_map:
        print 'sure' , key ,sure_map[key]
        return sure_map[key]
    return val

def merge():
    # sum1 = 0
    # for key in sure_map:
    #     sum1+= sure_map[key]
    # print sum1
    # return
    vec = []
    key2id = {}    
    for file in sys.argv[1:]:
        
        with open (file,'r') as f:
            cnt = 0 
            for L in f:
                
                disid,dayslice ,gap = L.strip().split(',')
                key  = disid+'-'+dayslice 
                if key in key2id:
                    vec[key2id[key]].append(gap)
                else:
                    key2id[key] = cnt 
                    vec.append([disid,dayslice,gap])
                cnt+=1

                    
    print ',',',',sys.argv[1:]
    for node in vec:
        vals = []
        for k in range(len(sys.argv[1:])):
            vals.append(node[2+k])
        print '{dis},{dayslice},{vals}'.format(
            dis=node[0],
            dayslice=node[1],
            vals=','.join(vals)
        )
    
    if len(sys.argv) == 3: #two files 
        ratio = [ abs((float(node[2]) -float( node[3])+0.)/float(node[3])) for node in vec ] 
        print 'ratio-mean=' , np.mean(ratio) , ' var= ' , np.var(ratio)
    ratio = []
    
    for moc in mer_out_conf:
        moc.append(open(moc[1],'w'))
    
    for node in vec:
        vals = []
        for k in range(len(sys.argv[1:])):
            vals.append(float(node[2+k]))
        ratio.append((node[0],node[1], (vals[1]-vals[0])/vals[0] ))
        #if abs(vals[1]-vals[0])/vals[0] > 10 or abs(vals[1]-vals[0]) > 100:
        
        if (vals[1] - vals[0])/vals[0] > 2 and vals[1] >50 :
            print 'bigger_val[0]<val[1]-{0}'.format(
                node[0]+','+node[1] in sure_map
            ),node[0],node[1],vals[0],vals[1] , (vals[1] - vals[0])/vals[0]
        if (vals[0] - vals[1])/vals[1] > 0.5:
            print 'val[0]>val[1]',node[0],node[1],vals[0],vals[1] , abs(vals[1] - vals[0])/vals[1]
        for moc in mer_out_conf:
            if moc[0] > 0:
                if (vals[1] - vals[0])/vals[0] > moc[0]:
                    val =vals[0]
                else:
                    val = vals[1]    #most of them are vals[1]
            else:

                if  (vals[1] - vals[0])/vals[1] < moc[0]:
                    val = vals[1]
                else:
                    val = vals[0]  #most of them are vals[0] i

            # if abs(vals[0]-vals[1w])/vals[0] > moc[0] :
            #     # print node[0],node[1],vals
            #     val = vals[0]
            # else:
            #     val = vals[1]
            #val= np.mean(vals)
            val = make_sure(node[0],node[1] ,val )
            moc[2].write( '{dis},{dayslice},{val}\n'.format(
                dis=node[0],
                dayslice=node[1],
                val=val
            ))
    for moc in mer_out_conf:
        moc[2].close()

    ratio = sorted(ratio,key=itemgetter(2),reverse=True)
    pivots = [1,  2, 5 ,10 ,20, 30 ] 
    cnts = [ 0 for i in pivots] 
    print ratio[0][2],ratio[len(ratio)-1][2]

    for node in ratio:
        for i in range(len(pivots)):
            if node[2]> pivots[i]:
                cnts[i] +=1 
    print zip(pivots, cnts)

if __name__ =='__main__':
    merge()
