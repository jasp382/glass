"""
Datetime Objects Management
"""

import datetime as dt


def now_as_int(utc=None):
    """
    Return Datetime.now as integer
    """
    
    _now = dt.datetime.now() if not utc else \
        dt.datetime.utcnow()
    
    now = int(_now.strftime('%Y%m%d%H%M%S'))
    
    return now


def now_as_str(utc=None):
    """
    Return Datetime.now as string
    """
    
    mapDic = {
        '00' : 'a',
        '01' : 'b', '02' : 'c', '03' : 'd', '04' : 'e', '05' : 'f', 
        '06' : 'g', '07' : 'h', '08' : 'i', '09' : 'j', '10' : 'k',
        '11' : 'l', '12' : 'm', '13' : 'n', '14' : 'o', '15' : 'p',
        '16' : 'q', '17' : 'r', '18' : 's', '19' : 't', '20' : 'u',
        '21' : 'v', '22' : 'w', '23' : 'x', '24' : 'y', '25' : 'z',
        '26' : '1', '27' : '2', '28' : '3', '29' : '4', '30' : '5',
        '31' : '6', '32' : '7', '33' : '8', '34' : '9', '35' : '0',
        '36' : '_a', '37' : '_c', '38' : '_d', '39' : '_e', '40' : '_f',
        '41' : '_g', '42' : '_h', '43' : '_i', '44' : '_j', '45' : '_k',
        '46' : '_l', '47' : '_m', '48' : '_n', '49' : '_o', '50' : '_p',
        '51' : '_q', '52' : '_r', '53' : '_s', '54' : '_t', '55' : '_u',
        '56' : '_v', '57' : '_w', '58' : '_x', '59' : '_y', '60' : '_z',
    }
    
    N = str(now_as_int(utc=utc))[2:]
    L = ''
    for c in range(0, len(N), 2):
        n = N[c:c+2]
        L += mapDic[n]
    
    return L


def now_as_unix(utc=None, retnotunix=None):
    """
    Returns now as Unix Timestamp
    """

    import time

    now = dt.datetime.now().replace(microsecond=0) \
        if not utc else dt.datetime.utcnow().replace(microsecond=0)
    
    unix = int(time.mktime(now.timetuple()))

    r = unix if not retnotunix else unix, now.strftime('%Y-%m-%d %H:%M:%S')

    return r


def day_to_intervals(interval_period):
    """
    Divide a day in intervals with a duration equal to interval_period
    
    return [
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ((lowerHour, lowerMinutes), (upperHour, upperMinutes)),
        ...
    ]
    """
    
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


def daysrange(firstday, lastday):
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
    all_days = ["{}-{}-{}".format(
        str(d.year),
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

