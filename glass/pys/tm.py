"""
Datetime Objects Management
"""


def now_as_int():
    """
    Return Datetime.now as integer
    """
    
    import datetime
    
    _now = str(datetime.datetime.now())
    
    _now = _now.replace('-', '')
    _now = _now.replace(' ', '')
    _now = _now.replace(':', '')
    _now = _now.split('.')[0]
    
    return int(_now)


def now_as_str():
    """
    Return Datetime.now as string
    """
    
    mapDic = {
        '00' : '9',
        '01' : 'a', '02' : 'b', '03' : 'c', '04' : 'd', '05'  : 'e', 
        '06' : 'f', '07' : 'g', '08' : 'h', '09' : 'i', '10' : 'j',
        '11' : 'k', '12' : 'l', '13' : 'm', '14' : 'n', '15' : 'o',
        '16' : 'p', '17' : 'q', '18' : 'r', '19' : 's', '20' : 't',
        '21' : 'u', '22' : 'v', '23' : 'w', '24' : 'x', '25' : 'y',
        '26' : 'z', '27' : 'A', '28' : 'B', '29' : 'C', '30' : 'D',
        '31' : 'E', '32' : 'F', '33' : 'G', '34' : 'H', '35' : 'I',
        '36' : 'J', '37' : 'K', '38' : 'L', '39' : 'M', '40' : 'N',
        '41' : 'O', '42' : 'P', '43' : 'Q', '44' : 'R', '45' : 'S',
        '46' : 'T', '47' : 'U', '48' : 'V', '49' : 'W', '50' : 'X',
        '51' : 'Y', '52' : 'Z', '53' : '1', '54' : '2', '55' : '3',
        '56' : '4', '57' : '5', '58' : '6', '59' : '7', '60' : '8',
    }
    
    N = str(now_as_int())[2:]
    L = ''
    for c in range(0, len(N), 2):
        n = N[c:c+2]
        L += mapDic[n]
    
    return L


def day_to_intervals(interval_period):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    return [
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ...
    ]
    """
    
    import datetime
    
    MINUTES_FOR_DAY = 24 * 60
    NUMBER_INTERVALS = MINUTES_FOR_DAY / interval_period
    
    hour = 0
    minutes = 0
    INTERVALS = []
    
    for i in range(NUMBER_INTERVALS):
        __minutes = minutes + interval_period
        __interval = (
            (hour, minutes),
            (hour + 1 if __minutes >= 60 else hour,
             0 if __minutes == 60 else __minutes - 60 if __minutes > 60 else __minutes)
        )
        
        INTERVALS.append(__interval)
        minutes += interval_period
        
        if minutes == 60:
            minutes = 0
            hour += 1
        
        elif minutes > 60:
            minutes = minutes - 60
            hour += 1
    
    return INTERVALS


def day_to_intervals2(intervaltime):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    intervaltime = "01:00:00"
    
    return [
        ('00:00:00', '01:00:00'), ('01:00:00', '02:00:00'),
        ('02:00:00', '03:00:00'), ...,
        ('22:00:00', '23:00:00'), ('23:00:00', '23:59:00')
    ]
    """
    
    from datetime import datetime, timedelta
    
    TIME_OF_DAY = timedelta(hours=23, minutes=59, seconds=59)
    DURATION    = datetime.strptime(intervaltime, "%H:%M:%S")
    DURATION    = timedelta(
        hours=DURATION.hour, minutes=DURATION.minute,
        seconds=DURATION.second
    )
    
    PERIODS = []
    
    upperInt = timedelta(hours=0, minutes=0, seconds=0)
    
    while upperInt < TIME_OF_DAY:
        if not PERIODS:
            lowerInt = timedelta(hours=0, minutes=0, seconds=0)
        
        else:
            lowerInt = upperInt
        
        upperInt = lowerInt + DURATION
        
        PERIODS.append((
            "0" + str(lowerInt) if len(str(lowerInt)) == 7 else str(lowerInt),
            "0" + str(upperInt) if len(str(upperInt)) == 7 else str(upperInt)
        ))
    
    PERIODS[-1] = (PERIODS[-1][0], '23:59:59')
    
    return PERIODS


def timerange(firstday, lastday):
    """
    Return a list with all days between firstday and lastday.

    Firstday and lastday must be strings like:
    YYYY-MM-DD
    """

    import datetime as dt

    f_year, f_month, f_day = firstday.split("-")
    l_year, l_month, l_day = lastday.split("-")

    # String to datetime
    fday = dt.date(int(f_year), int(f_month), int(f_day))
    lday = dt.date(int(l_year), int(l_month), int(l_day))

    # Days of difference
    ndays = lday - fday

    # Get days between 
    all_days = [fday] + [fday + dt.timedelta(
        days=i+1) for i in range(ndays.days)]
    
    # Convert days to string
    all_days = ["{}-{}-{}".format(str(d.year),
        str(d.month) if len(str(d.month)) == 2 else "0" + str(d.month),
        str(d.day) if len(str(d.day)) == 2 else "0" + str(d.day)
    ) for d in all_days]

    return all_days

def intervals_in_timerange(min_hour, max_hour, interval_duration):
    """
    Return intervals of X minutes in time range
    """

    import datetime as dt

    now = dt.datetime.now()

    intervals = [dt.datetime(now.year, now.month, now.day, min_hour, 0, 0)]
    last_dt = dt.datetime(now.year, now.month, now.day, max_hour, 0, 0)

    tst_dt = intervals[0]
    i  = 0

    while tst_dt < last_dt:
        intervals.append(intervals[i] + dt.timedelta(minutes=interval_duration))

        i += 1

        tst_dt = intervals[i]
    
    if intervals[-1] > last_dt:
        intervals = intervals[:-1]
    
    intervals = [t.time() for t in intervals]

    return intervals

