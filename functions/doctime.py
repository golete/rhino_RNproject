import datetime
import re

def doctime():
    time = str(datetime.datetime.now())
    timestamp = re.sub('\W',"",time)
    return timestamp[:8]+"_"+timestamp[8:14]
