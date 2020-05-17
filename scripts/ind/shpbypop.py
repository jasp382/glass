"""
Run shparea_by_mapunitpopulation
"""


from glass.ind.pop import shparea_by_mapunitpopulation


if __name__ == "__main__":
    shp = '/home/jasp/mystuff/rms/evu.shp'

    gunits = '/home/jasp/mystuff/rms/rms_freg_v3.shp'

    gunits_id = 'idfreg'

    out_col = 'evupop'

    output = '/home/jasp/mystuff/rms/rms_freg_v4.shp'

    pop_col = "pop11"

    shparea_by_mapunitpopulation(
        shp, gunits, gunits_id, out_col, output,
        units_pop=pop_col, areacol=None
    )

