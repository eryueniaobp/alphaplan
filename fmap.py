__author__ = 'baidu'


import sys ,re
from common import  sparse_feas
from operator import itemgetter
with open(sys.argv[1],'r') as f:

    idmap = []
    for L in f:
        fea ,id  = re.split('\s+',L.strip())
        id = int(id)
        if '=' in fea:
            key ,v  = fea.split('=') 
            if key in sparse_feas:
                idmap.append([id , fea , 'i'] ) 
                
        else:
            if fea in ['temp','pm25']:
                idmap.append([id,fea,'q'])   
            else:
                idmap.append([id,fea,'int'])   
    idmap.append([0 , 'ZERO','i'])         
    idmap  = sorted(idmap , key =itemgetter(0)  )
    for i in idmap:
        print '{id}\t{fea}\t{type}'.format(id=i[0],fea=i[1],type=i[2])
                


