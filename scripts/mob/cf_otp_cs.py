"""
Run OTP Closest facilities
"""

if __name__ == '__main__':
    import os
    from glass.mob.otp import otp_cf_based_on_rel
    from glass.pys.tm import intervals_in_timerange

    incidents = '/home/jasp/mrgis/gigs/bgri_pnt.shp'
    grpicol = 'idfreg'
    facilities = '/home/jasp/mrgis/gigs/ACESaude.shp'
    facilities_id = 'csid'

    rel_tbl = '/home/jasp/mrgis/gigs/freg_cs.xlsx'
    sheet = 'freg_cs'
    group_fk = 'codfreg'
    fac_fk = 'CS_FID'
    day = '09-21-2020'

    min_h = 8
    max_h = 20
    int_ = 15

    time_i = intervals_in_timerange(min_h, max_h, int_)
    time_str = ["{}:{}{}".format(
        str(t.hour) if t.hour < 13 else str(t.hour - 12),
        str(t.minute) if len(str(t.minute)) == 2 else '0' + str(t.minute),
        'pm' if t.hour > 12 else 'am'
    ) for t in time_i]

    output = '/home/jasp/mrgis/gigs/cf_otp_cs'
    bname = 'cs_'

    for h in time_str:
        otp_cf_based_on_rel(
            incidents, grpicol,
            facilities, facilities_id, rel_tbl, sheet, group_fk, fac_fk,
            h, day, os.path.join(output, bname + h.split(':')[0] + h.split(':')[1]  + '.shp')
        )

