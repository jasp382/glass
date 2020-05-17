"""
Time related
"""

def randomtime_to_shprows(in_shp, o_shp, start_date, end_date):
    """
    Relate time value to rows in one shapefile.

    The time is determined randomly from interval

    start_data and end_data must be datetime objects.
    """

    import datetime     as dt
    import random       as rdn
    from calendar       import monthrange
    from glass.ng.rd    import tbl_to_obj
    from glass.g.wt.shp import df_to_shp

    # Shape to Pandas.Dataframe
    gdf = tbl_to_obj(in_shp)

    # Get Random Dates
    def get_year(start, end):
        # Get Year
        if start.year == end.year:
            year = start.year
    
        else:
            year = rdn.randint(start.year, end.year)
    
        return year
    
    def get_month(start, end, year):
        # Get Month
        if start.year == end.year:
            if start.month == end.month:
                month = start.month
            else:
                month = rdn.randint(start.month, end.month)
    
        else:
            if year == start.year:
                month = rdn.randint(start.month, 12) if start.month < 12 else 12
        
            elif year == end.year:
                month = rdn.randint(1, end.month) if end.month > 1 else 1
    
        return month
    
    def get_day(s, e, y, m):
        # Get Day
        ndays = monthrange(y, m)[1]
    
        if s.year == e.year and s.month == e.month:
            if s.day == e.day:
                day = s.day
            else:
                day = rdn.randint(s.day, e.day)
    
        elif s.year == e.year and s.month != e.month:
            if m == s.month:
                day = rdn.randint(m, ndays)
            elif m == e.month:
                day = rdn.randint(1, e.day)
            else:
                day = rdn.randint(1, ndays)
    
        elif s.year != e.year:
            if y == s.year:
                if m == s.month:
                    day = rdn.randint(m, ndays)
                else:
                    day = rdn.randint(1, ndays)
            elif y == e.year:
                if m == e.month:
                    day = rdn.randint(1, e.day)
                else:
                    day = rdn.randint(1, ndays)
            else:
                day = rdn.randint(1, ndays)
    
        return day
    
    def get_hour(s, e, y, m, d):
        # Get Hour
        sDay = dt.datetime(s.year, s.month, s.day)
        eDay = dt.datetime(e.year, e.month, e.day)
        cDay = dt.datetime(y, m, d)
    
        if sDay == eDay:
            hour = rdn.randint(s.hour, e.hour)
        else:
            if sDay == cDay:
                hour = rdn.randint(s.hour, 23)
            elif eDay == cDay:
                hour = rdn.randint(0, e.hour)
            else:
                hour = rdn.randint(0, 23)
    
        return hour
    
    def get_minute(s, e, y, m, d, h):
        # Get minute
    
        sHour = dt.datetime(s.year, s.month, s.day, s.hour)
        eHour = dt.datetime(e.year, e.month, e.day, e.hour)
        cHour = dt.datetime(y, m, d, h)
    
        if sHour == eHour:
            minute = rdn.randint(s.minute, e.minute)
        else:
            if sHour == cHour:
                minute = rdn.randint(s.minute, 59)
            elif eHour == cHour:
                minute = rdn.randint(0, e.minute)
            else:
                minute = rdn.randint(0, 59)
    
        return minute
    
    def get_second(s, e, y, m, d, h, mi):
        # Get second
    
        sMinute = dt.datetime(s.year, s.month, s.day, s.hour, s.minute)
        eMinute = dt.datetime(e.year, e.month, e.day, e.hour, e.minute)
        cMinute = dt.datetime(y, m, d, h, mi)
    
        if sMinute == eMinute:
            second = rdn.randint(s.second, e.second)
        else:
            if sMinute == cMinute:
                second = rdn.randint(s.second, 59)
            elif eMinute == cMinute:
                second = rdn.randint(0, e.second)
            else:
                second = rdn.randint(0, 59)
        
        return second
    
    def sanitize(s):
        return "0{}".format(str(s)) if len(str(s)) == 1 else str(s)
    
    dates = []
    times = []
    for i in range(gdf.shape[0]):
        year = get_year(start_date, end_date)

        month = get_month(start_date, end_date, year)

        day = get_day(start_date, end_date, year, month)

        hour = get_hour(start_date, end_date, year, month, day)

        minute = get_minute(start_date, end_date, year, month, day, hour)

        second = get_second(start_date, end_date, year, month, day, hour, minute)

        month, day, hour, minute, second = [sanitize(i) for i in [month, day, hour, minute, second]]

        dates.append('{}-{}-{}'.format(year, month, day))
        times.append('{}:{}:{}'.format(hour, minute, second))
    
    # Set dates and times
    gdf['date'] = dates
    gdf['time'] = times

    # Export
    df_to_shp(gdf, o_shp)

    return o_shp

