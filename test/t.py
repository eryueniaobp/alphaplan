__author__ = 'baidu'

import re ,sys,datetime
# Difficult to sort too big file locally .as
# Instead we sort every day of the file .
def slice_to_hour(slice):
    slice =int(slice)
    return "{hour}:{minute}".format(hour=str((slice-1)/6).zfill(2)  ,  minute =  str((slice-1)%6 * 10 + 9).zfill(2) )

# 2016-01-01 21:56:29
def parse_time_slice(hourstr):
    print hourstr
    hour ,min , sec = hourstr.strip().split(':')
    hour = int(hour)
    min = int(min)
    sec = int(sec)
    return hour * 6 + min/10 +1
def iter_prev_dayslice(dayslice, num):
    day = dayslice[0:10]
    slice = dayslice.split('-')[-1]
    hourmin = slice_to_hour(slice)

    start_time = datetime.datetime.strptime(day+'-' + hourmin , '%Y-%m-%d-%H:%M')
    for i in range(num):
        curtime =  (start_time - datetime.timedelta(seconds=10*60*(i+1)))
        strt = curtime.strftime('%Y-%m-%d-%H:%M:%S')

        yield strt[0:10]+'-' + str(parse_time_slice(strt[11:]))

def main():
    for d in iter_prev_dayslice('2016-01-22-46', 3):
        print d



if __name__ == '__main__':
    main()