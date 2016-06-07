__author__ = 'baidu'
import sys , re
import  numpy as np
from merge import sure_map
def prefer(vec):
    ret = []
    for k in vec[2:]:
        avg = abs(k - vec[1])/vec[1]
        smart = abs(k - vec[0])/vec[0]
        if avg < smart:
            ret.append( 'avg')
        else:
            ret.append( 'smart')
    return ret


def detect():

    head = []
    risk_map = {}
    with open(sys.argv[1]) as f:  #csv
        for L in f:
            ws  = re.split(',' , L.strip())
            if len(head) == 0:
                head.extend(ws)
                print re.sub(',',',\t',L.strip())
            else:
                vec = [ float(i) for i in ws[2:]]
                if (vec[0] - vec[1])/vec[1] > 2 and vec [0] > 10: # risky
                    # if ws[0] +','+ws[1] not  in sure_map :
                    if prefer(vec)[0] == 'smart' and prefer(vec) != ['smart','smart','smart']  :
                        risk_map[ws[0]+','+ws[1]]  = vec[1] #avg
                        print re.sub(',',',\t',L.strip()) , prefer(vec) , ws[0] +','+ws[1] in sure_map , sure_map.get( ws[0] +','+ws[1],None )
    print risk_map


if __name__ == "__main__":
    detect()