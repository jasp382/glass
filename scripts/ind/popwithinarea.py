"""
Run pop_within_area
"""

from glass.ind.pop import pop_within_area


if __name__ == "__main__":
    gunits = '/home/jasp/rms/rms_mun_v8.shp'

    gunits_id = 'idmun'

    outcol = 'pruido65'

    sunits = '/home/jasp/rms/rms_bgri21.shp'

    sunits_id = 'bgri'

    popcol = 'pop21'

    gunits_fk = 'idmun'

    shp = '/home/jasp/rms/ruido_65ld_diss.shp'

    output = '/home/jasp/rms/rms_mun_v9.shp'

    pop_within_area(
        gunits, gunits_id, outcol, sunits,
        sunits_id, popcol, gunits_fk,
        shp, output,
        res_areas=None, res_areas_fk=None
    )

