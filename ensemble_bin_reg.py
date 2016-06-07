__author__ = 'baidu'


from sklearn import linear_model
import numpy as np
import ConfigParser,sys ,re
from solution_trend import  *

def correct(gap, divide_val , binval):
    if binval < 1 and gap < divide_val:
        return gap
    if binval >= 1 and gap > divide_val:
        return gap

    if binval == 0 and gap > divide_val:
        gap = divide_val/2
    if binval == 1 and gap < divide_val:
        gap = divide_val

    return gap


def ensemble():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    gap_bin = config.get('bingo','gap_bin')
    gap_reg = config.get('bingo','gap_reg')
    gap_ens = config.get('bingo','gap_ens')
    divide_val = float(config.get('train','gap_divide_val'))
    binpval = []
    with open(gap_bin,'r') as f:
        for L in f:

            val,pval = re.split('\s+',L.strip())
            binpval.append(float(pval))

    fw = open(gap_ens,'w')
    i = 0
    with open(gap_reg ,'r') as f:
        for L in f:
            disid ,ds , gap = re.split(',',L.strip())
            gap = float(gap)

            gap = correct(gap , divide_val , binpval[i] )
            fw.write('{disid},{ds},{val}\n'.format(
                disid = disid,
                ds=ds ,
                val = gap,
            ))
            i +=1

    fw.close()






if __name__ == '__main__':
    ensemble()