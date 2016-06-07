__author__ = 'baidu'

import subprocess,sys


for i in range(35):
    subprocess.check_call('sort -t, -k4 {file} >{file}.sorted &'.format(file=str(i).zfill(2)) ,shell=True)