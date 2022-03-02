"""
Procedures between views
"""

import os; import datetime
from gasp import __import
from rest_framework import status


def down_osm_by_geom(rqst_id, uid, geom_str):
    """
    Download OSM data using FORM Parameters
    """
    
    from django.contrib.gis.geos import GEOSGeometry
    from gasp.gt.to.rst          import geomext_to_rst_wShapeCheck
    from gasp.gt.prj             import proj
    from gasp.pyt.oss            import get_filesize
    from gasp.gt.to.osm          import download_by_boundary
    from gasp.g.to               import new_pnt, create_polygon
    from gasp.web.djg.mdl.w      import update_model
    from osmtolulc               import OSM_API, OSM_BOUNDARY
    from api.settings            import MODULES_DOMAIN
    from osmtolulc.models        import rqsts, lyr, lyr_feat
    
    # Get Geometry Object
    points = geom_str.replace('d', '.').split('pv')
    for p in range(len(points)):
        x, y      = points[p].split('s')
        points[p] = new_pnt(x, y)
    
    POLYGON      = create_polygon(points)
    POLYGON_3857 = proj(POLYGON, None, 3857, inEPSG=4326, gisApi='OGRGeom')
    
    REF_RASTER = geomext_to_rst_wShapeCheck(
        POLYGON_3857, 35000000, [2, 3, 3.5, 4, 5, 8, 10],
        os.path.join(OSM_BOUNDARY, 'ref_{}.tif'.format(rqst_id)), 3857)
    
    POLYGON_3857.FlattenTo2D()
    
    # Update RQST and LYR table
    rqstInst = rqsts.objects.create(fid=rqst_id, user_id=int(uid))
    
    LYR_ID = rqst_id + '_1'
    lyrInst = lyr.objects.create(
        fid=LYR_ID, rqst=rqstInst, slug='areai',
        name='Area of Interest', lyrt='geojson', style='boundary',
        url='{}/api/rest/osmtolulc/feat/{}/'.format(
            MODULES_DOMAIN, LYR_ID
        ),
        dw_url = '{}/api/rest/osmtolulc/down/{}/'.format(
            MODULES_DOMAIN, LYR_ID
        )
    )
    
    featInst = lyr_feat.objects.create(
        fid=rqst_id + '_11', lyr=lyrInst,
        geom=GEOSGeometry(POLYGON_3857.ExportToWkt(), srid=3857)
    )
    
    if not REF_RASTER:
        # Return Error
        # Area selected is to big
        
        rqstInst.status = '102'
        rqstInst.save()
        
        return 102, rqst_id
    
    """
    Download OSM data using OSM Overpass API
    """
    OSM_FILE = download_by_boundary(
        POLYGON, OSM_API, 'osm_{}'.format(rqst_id),
        4326, GetUrl=None)
    
    FILESIZE = fprop(OSM_FILE, 'fs', fs_unit="MB")
    rqstInst.filesize = FILESIZE
    
    if FILESIZE <= 500:
        status = '101'
    else:
        status = '102'
    
    rqstInst.status = status
    
    rqstInst.save()
    
    return int(status), rqst_id


def prod_down_osm_by_geom(RQST, USER_ID, GEOM):
    """
    Download OSM data - mechanism to deal with exceptions
    """
    
    try:
        STAT, RQST_ID = down_osm_by_geom(RQST, USER_ID, GEOM)
        
        return STAT, RQST_ID
    
    except Exception:
        import sys, traceback
        from django.contrib.gis.geos import GEOSGeometry
        from gasp.g.to               import new_pnt, create_polygon
        from gasp.gt.prj             import proj
        from api.settings            import MODULES_DOMAIN
        from osmtolulc.models        import rqsts, lyr, lyr_feat
        
        ERROR_LST = traceback.format_exc().splitlines()
        ERROR_STR = "|".join(ERROR_LST)
        
        # Write data in database
        # - Get Geometry Object
        points = GEOM.replace('d', '.').split('pv')
        for p in range(len(points)):
            x, y      = points[p].split('s')
            points[p] = new_pnt(x, y)
        
        POLYGON      = create_polygon(points)
        POLYGON_3857 = proj(POLYGON, None, 3857, inEPSG=4326, gisApi='OGRGeom')
        POLYGON_3857.FlattenTo2D()
        
        rqstsI = rqsts.objects.filter(fid=RQST)
        
        if not len(rqstsI):
            STATUS = '104'
            
            rIns = rqsts.objects.create(
                fid=RQST, user_id=int(USER_ID), status=STATUS,
                error=ERROR_STR
            )
            
            lyr_id = RQST + '_1'
            lIns = lyr.objects.create(
                fid=lyr_id, rqst=rIns, slug='areai',
                name='Area of Interest', lyrt='geojson',
                style='boundary',
                url='{}/api/rest/osmtolulc/feat/{}/'.format(
                    MODULES_DOMAIN, lyr_id
                ),
                dw_url='{}/api/rest/osmtolulc/down/{}/'.format(
                    MODULES_DOMAIN, lyr_id
                )
            )
            
            featI = lyr_feat.objects.create(
                fid=RQST+'_11', lyr=lIns,
                geom=GEOSGeometry(POLYGON_3857.ExportToWkt(), srid=3857)
            )
        
        else:
            STATUS = '107'
            
            rIns = rqstsI[0]
            rIns.status = STATUS
            rIns.error = ERROR_STR
            rIns.save()
        
        return STATUS, RQST


def go_osm2lulc(RQST_FID, NOMENCLA):
    """
    Run OSM2LULC Procedure
    """
    
    from api.settings           import GEOSERVER_SETT, MODULES_DOMAIN
    from osmtolulc              import OSM_API, OSM_BOUNDARY, LULC_RESULT, OSM_SLD
    from osmtolulc.models       import rqsts, lyr
    from osgeo                  import ogr
    from gasp.pyt.oss           import create_folder
    from gasp.alg.osm2lulc.num  import osm2lulc
    from gasp.gt.prj            import set_proj
    from gasp.gt.to.rst         import shpext_to_rst
    from gasp.web.geosrv.ws     import lst_ws
    from gasp.web.geosrv.stores import add_rst_store
    from gasp.web.geosrv.lyrs   import pub_rst_lyr
    from gasp.web.geosrv.sty    import create_style
    from gasp.web.geosrv.sty    import assign_style_to_layer
    
    REF_RASTER = os.path.join(
        OSM_BOUNDARY, 'ref_{}.tif'.format(RQST_FID)
    )
    
    lulc_map_folder = mkdir(os.path.join(LULC_RESULT, RQST_FID))
    
    # Get TIME A
    time_a = datetime.datetime.now().replace(microsecond=0)
    
    lulcMap, meta_time = osm2lulc(
        os.path.join(OSM_API, 'osm_{}.xml'.format(RQST_FID)),
        NOMENCLA, REF_RASTER,
        os.path.join(
            lulc_map_folder, '{}.tif'.format(RQST_FID)
        ), overwrite=True, roadsAPI='POSTGIS'
    )
    
    # Get TIME B
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    # Send Data to GEOSERVER
    set_proj(lulcMap, 3857)
    
    GEOSRV_WORK = "lulc_results"
    GEOSRV_WORKS = lst_ws(conf=GEOSERVER_SETT)
    
    if GEOSRV_WORK not in GEOSRV_WORKS:
        from gasp.web.geosrv.ws import create_ws
        create_ws(GEOSRV_WORK, conf=GEOSERVER_SETT, overwrite=True)
    
    add_rst_store(
        lulcMap, 'store_{}'.format(RQST_FID),
        GEOSRV_WORK, conf=GEOSERVER_SETT
    )
    
    pub_rst_lyr(
        "lulc_layer_{}".format(RQST_FID),
        'store_{}'.format(RQST_FID),
        GEOSRV_WORK, 3857, conf=GEOSERVER_SETT
    )
    
    # Create style
    STYLE_NAME = "lulc_style_{}".format(RQST_FID)
    create_style(
        STYLE_NAME, OSM_SLD[NOMENCLA],
        conf=GEOSERVER_SETT, overwrite=False
    )
    
    LYR_NAME = "lulc_layer_{}".format(RQST_FID)
    assign_style_to_layer(STYLE_NAME, LYR_NAME, conf=GEOSERVER_SETT)
    
    # Update RQSTS model
    rqstInst = rqsts.objects.get(fid=RQST_FID)
    
    rqstInst.nomenclature = NOMENCLA
    rqstInst.date         = time_a.date()
    rqstInst.start_time   = time_a.time()
    rqstInst.end_time     = time_b.time()
    rqstInst.status       = '105'
    
    rqstInst.save()
    
    # Update LYR model
    LYR_ID = RQST_FID + '_2'
    lyrInst = lyr.objects.create(
        fid=LYR_ID, rqst=rqstInst, slug='lulcm',
        name='LULC Map', lyrt='geoserver', lname=LYR_NAME,
        style=STYLE_NAME, url='{}://{}:{}/geoserver/ows?'.format(
            GEOSERVER_SETT['PROTOCOL'], GEOSERVER_SETT['HOST'],
            GEOSERVER_SETT['PORT']
        ),
        dw_url='{}/api/rest/osmtolulc/geotif/{}/'.format(
            MODULES_DOMAIN, RQST_FID
        )
    )
    
    #del MDL_INSTANCE, modelCls
    
    return 105, RQST_FID


def prod_go_osm2lulc(rqst, nomenclature):
    """
    Run OSM2LUC dealing with exceptions
    """
    
    try:
        STATUS, RFID = go_osm2lulc(rqst, nomenclature)
        
        return STATUS, RFID
    
    except Exception:
        """
        Deal with exception
        """
        
        import traceback;     import datetime
        from osmtolulc.models import rqsts
        
        ERROR_LST = traceback.format_exc().splitlines()
        ERROR_STR = "|".join(ERROR_LST)
        
        RQST_INSTANCE = rqsts.objects.get(fid=rqst)
        
        # Write data in the database
        time_b = datetime.datetime.now().replace(microsecond=0)
        
        RQST_INSTANCE.error = ERROR_STR[:10000]
        RQST_INSTANCE.nomenclature = nomenclature
        RQST_INSTANCE.date         = time_b.date()
        RQST_INSTANCE.end_time     = time_b.time()
        RQST_INSTANCE.status       = '106'
        
        RQST_INSTANCE.save()
        
        del RQST_INSTANCE
        
        return 106, rqst
