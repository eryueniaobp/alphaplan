__author__ = 'baidu'
import sys

from merge import sure_map
def make_sure( disid, dayslice ,val ,sure_map):

    key = disid +',' + dayslice
    if key in sure_map:
        # print 'sure' , key ,sure_map[key]
        return sure_map[key]
    return val
risk_map = {
    '8,2016-01-28-58':40.6161,
    '28,2016-01-22-130':35.9614,
    '24,2016-01-28-58': 26.0483,
    '7,2016-01-28-118':33.8329,
}
# if (vec[0] - vec[1])/vec[1] > 2 and vec [0] > 10: # risky
#                     # if ws[0] +','+ws[1] not  in sure_map :
#                     if prefer(vec)[0] == 'smart' and prefer(vec) != ['smart','smart','smart']  :
#                         risk_map[ws[0]+','+ws[1]]  = vec[1] #avg
risk_map.update(
    {'20,2016-01-28-130': 5.2, '9,2016-01-26-58': 5.75,
     '28,2016-01-22-130': 23.65,
     '13,2016-01-26-58': 1.35,
     '42,2016-01-22-70': 3.45,
     '26,2016-01-26-130': 10.55,
     '4,2016-01-28-130': 6.1,
     '35,2016-01-28-118': 4.4,
     '14,2016-01-24-70': 7.7,
     '7,2016-01-28-118': 24.65,
     '8,2016-01-28-58': 58.9,
     '29,2016-01-22-70': 3.55,
     '16,2016-01-28-82': 1.0,
     '24,2016-01-28-58': 38.9,
     '26,2016-01-26-58': 14.05,
     '31,2016-01-26-58': 2.3,
     '29,2016-01-24-58': 4.45,
     '29,2016-01-24-70': 3.55,
     '41,2016-01-26-58': 2.35,
     '41,2016-01-22-58': 2.35, '28,2016-01-26-70': 5.6, '47,2016-01-30-58': 2.5, '7,2016-01-24-58': 5.0, '20,2016-01-30-82': 4.6}
)
def hand():
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

                disid,dayslice ,val = L.strip().split(',')
                key  = disid+'-'+dayslice
                vec = [float(val)]
                val = float(make_sure(disid,dayslice,val,sure_map))
                if vec[0] != val:
                    vec.append(val)
                    # print vec
                # val = make_sure(disid,dayslice,val , risk_map)
                # val = gap

                # if float(val) > 200:
                #     val = 1.0
                print '{disid},{ds},{val}'.format(disid= disid,ds = dayslice,val = val)




if __name__ =='__main__':
    hand()
