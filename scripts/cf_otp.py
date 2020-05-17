"""
Run OTP Closest facilities
"""

if __name__ == '__main__':
    import os
    from glass.g.mob.otp import otp_closest_facility
    from glass.pys.tm import intervals_in_timerange

    """
    Parameters
    """
    incidents  = '/home/jasp/mrgis/bgri_pnt.shp'
    facilities = '/home/jasp/mrgis/Escolas.shp'
    date= '09-21-2020'

    min_h = 7
    max_h = 10
    int_  = 15

    time_i = intervals_in_timerange(min_h, max_h, int_)
    time_str = ["{}:{}{}".format(
        str(t.hour) if t.hour < 13 else str(t.hour - 12),
        str(t.minute) if len(str(t.minute)) == 2 else '0' + str(t.minute),
        'pm' if t.hour > 12 else 'am'
    ) for t in time_i]

    output = '/home/jasp/mrgis'
    bname = 'esc_'

    """
    Run Script
    """

    for h in time_str:
        otp_closest_facility(
            incidents, facilities, h, date,
            os.path.join(
                output,
                bname + h.split(':')[0] + h.split(':')[1]  + '.shp'
            )
        )

