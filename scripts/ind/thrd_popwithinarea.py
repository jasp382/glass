"""
Run pop_within_area
"""

from glass.ind.thrd.pop import thrd_popwithinarea


if __name__ == "__main__":
    gunits = '/home/jasp/rms/muns'

    gunits_id = 'idmun'

    outcol = 'pruido55'

    sunits = '/home/jasp/rms/bgribymun'

    sunits_id = 'refid'

    popcol = 'popres'

    gunits_fk = 'idmun'

    shp = '/home/jasp/rms/r55mun'

    output = '/home/jasp/rms/res'

    oname = 'pruido55'

    thrd_popwithinarea(
        gunits, gunits_id, outcol, sunits,
        sunits_id, popcol, gunits_fk,
        shp, output, oname
    )

