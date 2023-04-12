"""
Run shparea_by_mapunitpopulation
"""


from glass.ind.pop import shparea_by_mapunitpopulation


if __name__ == "__main__":
    shp = '/home/jasp/rms/evu.shp'

    gunits = '/home/jasp/rms/rms_mun_v5.shp'

    gunits_id = 'idmun'

    out_col = 'evuhab'

    output = '/home/jasp/rms/rms_mun_v6.shp'

    pop_col = "pop21"

    shparea_by_mapunitpopulation(
        shp, gunits, gunits_id, out_col, output,
        units_pop=pop_col, areacol=None
    )

