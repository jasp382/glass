"""
Rule 5 - Basic buffer
"""

import os
import datetime as dt

from glass.ete.osm2lulc import DB_SCHEMA

def basic_buffer(osmdb, lineTable, dataFolder, apidb='SQLITE'):
    """
    Data from Lines table to Polygons using a basic buffering stratagie
    """
    
    import datetime
    from glass.sql.q                import q_to_obj
    if apidb == 'POSTGIS':
        from glass.gp.prox.bfing.sql import st_buffer
    else:
        from glass.gp.prox.bfing.sql import splite_buffer as st_buffer
    from glass.dtt.torst              import grsshp_to_grsrst as shp_to_rst
    from glass.it.shp                import shp_to_grs
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = q_to_obj(osmdb, (
        "SELECT basic_buffer FROM {} WHERE basic_buffer IS NOT NULL "
        "GROUP BY basic_buffer"
    ).format(
        lineTable
    ), db_api='psql' if apidb=='POSTGIS' else 'sqlite').basic_buffer.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        # Run BUFFER Tool
        time_x = datetime.datetime.now().replace(microsecond=0)
        bb_file = st_buffer(
            osmdb, lineTable, "bf_basic_buffer", "geometry",
            os.path.join(dataFolder, 'bb_rule5_{}.shp'.format(str(int(cls)))),
            whrClause="basic_buffer={}".format(str(int(cls))),
            outTblIsFile=True, dissolve="ALL", cols_select="basic_buffer"
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        # Data TO GRASS
        grsVect = shp_to_grs(
            bb_file, "bb_{}".format(int(cls)), asCMD=True,
            filterByReg=True
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        # Data to Raster
        rstVect = shp_to_rst(
            grsVect, int(cls), f"rbb_{int(cls)}", 
            cmd=True
        )
        time_w = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(cls)] = rstVect
        
        timeGasto[tk]   = ('do_buffer_{}'.format(cls), time_y - time_x)
        timeGasto[tk+1] = ('import_{}'.format(cls), time_z - time_y)
        timeGasto[tk+2] = ('torst_{}'.format(cls), time_w - time_z)
        
        tk += 3
    
    return clsRst, timeGasto


def num_base_buffer(osmdb, lineTbl, folder, cells, srscode, rtemplate,
                    api='SQLITE'):
    """
    Data from Lines to Polygons
    """
    
    import datetime
    from threading            import Thread
    from glass.sql.q       import q_to_obj
    if api=='SQLITE':
        from glass.gp.prox.bfing.sql import splite_buffer as st_buffer
    else:
        from glass.gp.prox.bfing.sql import st_buffer
    from glass.dtt.torst              import shp_to_rst
    
    # Get LULC Classes to be selected
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = q_to_obj(osmdb, (
        "SELECT basic_buffer FROM {} WHERE basic_buffer IS NOT NULL "
        "GROUP BY basic_buffer"
    ).format(
        lineTbl
    ), db_api='psql' if api == 'POSTGIS' else 'sqlite').basic_buffer.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    clsRst = {}
    
    def exportAndBufferB(CLS, cnt):
        # Run BUFFER Tool
        time_x = datetime.datetime.now().replace(microsecond=0)
        bb_file = st_buffer(
            osmdb, lineTbl, "bf_basic_buffer", "geometry",
            os.path.join(folder, 'bb_rule5_{}.shp'.format(str(int(CLS)))),
            whrClause="basic_buffer={}".format(str(int(CLS))),
            outTblIsFile=True, dissolve=None, cols_select="basic_buffer"
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        # To raster
        rstCls = shp_to_rst(
            bb_file, None, cells, 0,
            os.path.join(folder, 'rst_bbfr_{}.tif'.format(CLS)),
            epsg=srscode, rst_template=rtemplate, api='gdal'
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[CLS] = rstCls
        timeGasto[cnt + 1] = ('buffer_{}'.format(str(CLS)), time_y - time_x)
        timeGasto[cnt + 2] = ('torst_{}'.format(str(CLS)), time_z - time_y)
    
    thrds = [Thread(
        name="r5-{}".format(lulcCls[i]), target=exportAndBufferB,
        args=(lulcCls[i], (i+1) * 10)
    ) for i in range(len(lulcCls))]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    return clsRst, timeGasto


def water_lines_to_polygon():
    """
    Convert OSM Lines to Polygons expressing existence of water bodies
    with the help of Sattelite imagery and Normalized Difference Watter
    Index.
    """
    
    """
    Procedure:
    1 - Apply NWDI
    2 - Reclassify: Water - 1; No Water - NoData
    3 - Region Group
    4 - See if Water Lines overlap Water Regions and which regions
    4.1 - Regions overlaped with Water Lines are considered as water bodies
    """
    
    return None


def osmwater_vs_ndwi(water, ndwi, oshp):
    """
    """

    import os

    from glass.wenv.grs import run_grass
    from glass.pys.oss import mkdir, fprop
    from glass.pys.tm import now_as_str

    # Prepare workspace
    ws, loc = mkdir(os.path.join(
        os.path.dirname(oshp),
        now_as_str(utc=True) 
    ), overwrite=True), 'locwork'

    # Start GRASS GIS Session
    gb = run_grass(ws, location=loc, srs=ndwi)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    # GRASS GIS Modules
    from glass.it.shp import shp_to_grs, grs_to_shp
    from glass.it.rst import rst_to_grs
    from glass.rst.alg import grsrstcalc


    return oshp

