"""
OSM2LULC Priority Rule
"""

import datetime as dt
from glass.ete.otol.vec import priority_rule


if __name__ == "__main__":
    shp = '/home/jasp/osmpr/terceira.gpkg'

    refraster = '/home/jasp/osmpr/rst_terceira.tif'

    lyr = 'osmtolulc_v2'

    col = 'lulc'

    osm_db = 'terceira'

    time_a = dt.datetime.now().replace(microsecond=0)

    priority_rule(shp, lyr, refraster, col, osm_db)

    time_b = dt.datetime.now().replace(microsecond=0)

    print(f"Total time: {time_b - time_a}")

