
from __future__ import division
from datetime import datetime, timedelta

def totimestamp(dtstr, epoch=datetime(1970,1,1)):
    '''2019-03-31 16:38:37'''
    dt = datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S')
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

type(totimestamp(datetime_object))