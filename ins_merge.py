__author__ = 'baidu'
from  itertools  import  groupby
import sys , subprocess, re,datetime
from operator import itemgetter
import ConfigParser

#merge data

def read_from_file(file, separator):
    with open(file , 'r') as f:
        for line in f:
            # print line
            yield line.strip().split(separator)

def main():
    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])
    phase = sys.argv[2]

    insfile = config.get(phase,'ins_path')
    insmergefile= config.get(phase,'ins_merge_path')

    print 'begin '
    # subprocess.check_call('sort -t, -k4 {file} >{file}.sorted'.format(file=insfile) , shell=True)
    print 'sort ok'
    merge_file = open('{file}'.format(file=insmergefile) , 'w')

    data = read_from_file('{file}.sorted'.format(file=insfile), ',')
    for key,group in groupby(data,key=itemgetter(3)):
        sup = 0
        dem = 0
        gap = 0

        for node in group:
            sup += int(node[0])
            dem += int(node[1])
            gap += int(node[2])
        vec = []
        vec.append(str(sup))
        vec.append(str(dem))
        vec.append(str(gap))
        vec.extend(node[3:])

        merge_file.write(','.join(vec) +'\n')
    merge_file.flush()
    merge_file.close()
    print 'merge ok'

if __name__ == '__main__':
    main()