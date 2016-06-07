__author__ = 'baidu'
import re,sys
import numpy as np
import ConfigParser
from operator import itemgetter

def diffgap():
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


    # print ',',',',sys.argv[1:]
    # for node in vec:
    #     vals = []
    #     for k in range(len(sys.argv[1:])):
    #         vals.append(node[2+k])
    #     # print '{dis},{dayslice},{vals}'.format(
    #     #     dis=node[0],
    #     #     dayslice=node[1],
    #     #     vals=','.join(vals)
    #     # )

    # if len(sys.argv) == 3: #two files
    #     ratio = [ abs((float(node[2]) -float( node[3])+0.)/float(node[3])) for node in vec ]
    #     print 'ratio-mean=' , np.mean(ratio) , ' var= ' , np.var(ratio)
    ratio = []



    for node in vec:
        vals = []
        for k in range(len(sys.argv[1:])):
            vals.append(float(node[2+k]))
        if vals[0] != vals[1] :
            print node[0],node[1] ,vals[0],vals[1]
        # ratio.append((node[0],node[1], (vals[1]-vals[0])/vals[0] ))
        #if abs(vals[1]-vals[0])/vals[0] > 10 or abs(vals[1]-vals[0]) > 100:

if __name__ =='__main__':
    diffgap()
