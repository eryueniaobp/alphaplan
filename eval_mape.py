__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
import ConfigParser,logging





def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])


    eval_ret = config.get('train','eval_mape' )

    vec = []
    with open(eval_ret, 'r') as f:
        for L in f:
            val , pred = re.split('\s+',L.strip())
            val ,pred = float(val) ,max(1, float(pred))
            if val != 0:
                vec.append([val,pred])

    mape =  sum([ abs(i[1] - i[0])/i[0] for i in vec ]) /len(vec)
    print 'mape: ' , mape  , ' len=' , len(vec)
    logging.info( 'done' )

    # idlization ::
if __name__ == '__main__':
    main()
