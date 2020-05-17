"""
Run pop_within_area
"""

from glass.ind.pop import pop_within_area


if __name__ == "__main__":
    gunits = '/home/jasp/mystuff/rms/rms_mun_v7.shp'

    gunits_id = 'idmun'

    outcol = 'pruido55'

    sunits = '/home/jasp/mystuff/rms/rms_bgri.shp'

    sunits_id = 'refid'

    popcol = 'popres'

    gunits_fk = 'idmun'

    shp = '/home/jasp/mystuff/rms/ruido_55ld_Diss.shp'

    output = '/home/jasp/mystuff/rms/rms_mun_v8.shp'

    pop_within_area(
        gunits, gunits_id, outcol, sunits,
        sunits_id, popcol, gunits_fk,
        shp, output,
        res_areas=None, res_areas_fk=None
    )