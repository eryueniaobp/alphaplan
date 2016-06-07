__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser,logging
from data_transform import  slice_to_hour
from data_transform import distance
# fit the liblinear format .


def get_pred(file):
    vec = []
    with open(file ,'r') as f:
        for L in f:
            val , pred = re.split('\s+',L.strip())
            vec.append(pred)
    return vec
def normalize(val):
    val = float(val)
    ret = val
    if val < 1:
        ret = 1
    return ret


def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])


    result = config.get('prediction','result' )
    sup = config.get('bingo','sup')
    dem = config.get('bingo','dem')
    gap = config.get('bingo','gap')

    sup_vec = get_pred(sup)
    dem_vec = get_pred(dem)
    gap_vec = get_pred(gap)
    gap_sum_0 = 0 
    gap_sum_1 = 0 
    gap_sum_2 = 0
    gap_sum_3 = 0
    with open(config.get('bingo','result'),'w') as w:
        with open(result,'r') as f:
            i = 0
            for L in f:
                distid ,dayslice ,val = re.split(',',L.strip())
                val = float(dem_vec[i]) - float(sup_vec[i])

                gapval = gap_vec[i]

                i+= 1
                
                gap_sum_0 += val 
                gap_sum_1 += float(gapval)
                gap_sum_2 += normalize(val)
                gap_sum_3 += normalize(gapval)
                w.write('{id},{dayslice},{gap},{gap_0}\n'.format(
                    id=  distid ,
                    dayslice=dayslice,
                    gap= normalize(val) ,
                    gap_0 = normalize(gapval)
                ))








    print gap_sum_0,gap_sum_1,gap_sum_2,gap_sum_3 ,gap_sum_2/2838,gap_sum_3/2838
    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()
