"""
Run OSM2LULC
"""

if __name__ == '__main__':
    import os
    import codecs
    import datetime as dt
    from gasp.sds.osm2lulc.utils import record_time_consumed
    from gasp.pyt.oss import fprop

    """
    Input Parameters
    """

    VERSION      = 'v14'
    NOMENCLATURE = "CORINE_LAND_COVER"
    OSMDATA      = '/home/jasp/mrgis/osmtolulc/osm_brussels_01.xml'
    REF_FILE     = '/home/jasp/mrgis/osmtolulc/lmt_brussels_01.shp'
    LULC_RESULT  = '/home/jasp/mrgis/osmtolulc/lc_brussels_01_v14.tif'
    DATA_STORE   = '/home/jasp/mrgis/osmtolulc/tmp_brussels01_v14'

    """
    Run OSM2LULC
    """
    time_a = dt.datetime.now().replace(microsecond=0)

    if VERSION == 'v14':
        from gasp.sds.osm2lulc.num import osm2lulc

        result, timeobj = osm2lulc(
            OSMDATA, NOMENCLATURE, REF_FILE, LULC_RESULT,
            overwrite=True, dataStore=DATA_STORE
        )
    
    elif VERSION == 'v13':
        from gasp.sds.osm2lulc.grs import raster_based

        result, timeobj = raster_based(
            OSMDATA, NOMENCLATURE, REF_FILE, LULC_RESULT,
            overwrite=True, dataStore=DATA_STORE
        )
    
    else:
        from gasp.sds.osm2lulc.grs import vector_based

        result, timeobj = vector_based(
            OSMDATA, NOMENCLATURE, REF_FILE, LULC_RESULT,
            overwrite=True, dataStore=DATA_STORE,
            RoadsAPI='POSTGIS' if VERSION == 'v12' else 'GRASS'
        )
    
    time_b = dt.datetime.now().replace(microsecond=0)
    
    """
    Record time consumed
    """

    record_time_consumed(timeobj, os.path.join(
        os.path.dirname(LULC_RESULT), fprop(LULC_RESULT, 'fn') + '.xlsx'
    ))

    total_time = os.path.join(
         os.path.dirname(LULC_RESULT), fprop(LULC_RESULT, 'fn') + '.txt'
    )
    with codecs.open(total_time, 'w', encoding='utf-8') as f:
        f.write(str(time_b - time_a))

