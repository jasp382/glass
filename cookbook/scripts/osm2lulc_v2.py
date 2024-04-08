"""
Run OSM2LULC
"""

import os
import datetime
from glass.pys.oss import fprop
from glass.ete.osm2lulc.grs import vector_based
from glass.ete.osm2lulc.utils import record_time_consumed


if __name__ == '__main__':
    NOMENCLATURE = "EURO_TEST"
    OSMDATA      = '/mnt/disk1/jasp/osm2lulc/osm_parts/osmbasel_{}.xml'
    REF_RASTER   = '/mnt/disk1/jasp/osm2lulc/lmt_basel/fishnet_basel_{}.shp'
    LULC_RESULT  = '/mnt/disk1/jasp/osm2lulc/lulc_basel/lu_basel_{}.shp'
    DATA_STORE   = '/mnt/disk1/jasp/osm2lulc/tmp_basel/tmpbs_{}'

    # Run OSM2LULC
    for i in range(25):
        time_a = datetime.datetime.now().replace(microsecond=0)
    
        lulcSHP, timeCheck = vector_based(
            OSMDATA.format(str(i+1)), NOMENCLATURE,
            REF_RASTER.format(str(i+1)), LULC_RESULT.format(str(i+1)),
            overwrite=True, dataStore=DATA_STORE.format(str(i+1)),
            RoadsAPI='POSTGIS'
        )
    
        time_b = datetime.datetime.now().replace(microsecond=0)
    
        # Record time consumed in xlsx table
        record_time_consumed(timeCheck, os.path.join(
            os.path.dirname(lulcSHP), fprop(lulcSHP, 'fn') + '.xlsx'
        ))

        print(time_b - time_a)

