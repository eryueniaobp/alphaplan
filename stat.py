__author__ = 'baidu'



import re,sys
from data_transform import load_cluster_map
def main():
    cluster_map = {}
    load_cluster_map(sys.argv[2],cluster_map)
    print len(cluster_map)
    srcmap = {}
    dstmap = {}
    gapmap = {}
    cnt = 0
    gap_cnt = 0.
    with open(sys.argv[1] , 'r') as f:
        for L in f:
            cnt +=1.
            ws = re.split('\s+',L.strip())
            srcmap[ws[3]] = srcmap.get(ws[3] ,0 ) +1
            dstmap[ws[4]] = dstmap.get(ws[4] ,0 ) +1

            gap = 0
            if ws[1] == 'NULL':
                gap =1
            gap_cnt += gap
            gapmap[ws[3]]  = gapmap.get(ws[3] , 0) +gap
    print len(srcmap) ,len(dstmap)
    for key in srcmap:
        print cluster_map.get(key,-1) , key ,gapmap[key] , srcmap[key],dstmap.get(key,0),gapmap[key]/gap_cnt, srcmap[key]/cnt ,dstmap.get(key,0)/cnt


if __name__ == '__main__':
    main()
