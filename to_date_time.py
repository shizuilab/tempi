def to_date_time(data):

    tmp = data[0:2]
    yyyy = int.from_bytes(tmp,'little')

    mm = int(data[2])
    dd = int(data[3])
    hh = int(data[4])
    min = int(data[5])
    ss = int(data[6])

    strdate_time=str(yyyy)+"/"+str(mm)+"/"+str(dd)+" "+str(hh)+":"+str(min)+":"+str(ss)
    return strdate_time
