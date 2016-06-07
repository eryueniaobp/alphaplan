__author__ = 'baidu'

import sys

def shrink():
    # sum1 = 0
    # for key in sure_map:
    #     sum1+= sure_map[key]
    # print sum1
    # return
    vec = []
    key2id = {}

    alpha = float(sys.argv[2])
    file  =  sys.argv[1]

    with open (file,'r') as f:
        cnt = 0
        for L in f:

            disid,dayslice ,val = L.strip().split(',')


            val = max(1, float(val) * alpha)
            print '{disid},{ds},{val}'.format(disid= disid,ds = dayslice,val = val)


if __name__ =='__main__':
    shrink()