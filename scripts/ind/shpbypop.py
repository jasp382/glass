"""
Run shparea_by_mapunitpopulation
"""


from glass.ind.pop import shparea_by_mapunitpopulation


if __name__ == "__main__":
    shp = '/home/jasp/rms/rms_greenvf.shp'

    gunits = '/home/jasp/rms/rms_freg_v1.shp'

    gunits_id = 'idfreg'

    out_col = 'greenhab'

    output = '/home/jasp/rms/rms_freg_v2.shp'

    pop_col = "pop2021"

    shparea_by_mapunitpopulation(
        shp, gunits, gunits_id, out_col, output,
        units_pop=pop_col, areacol=None
    )

