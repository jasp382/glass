"""
Rule 5 - Basic buffer
"""

import os
from glass.ete.osm2lulc import DB_SCHEMA

def basic_buffer(osmdb, lineTable, dataFolder, apidb='SQLITE'):
    """
    Data from Lines table to Polygons using a basic buffering stratagie
    """
    
    import datetime
    from glass.dct.sql.fm       import q_to_obj
    if apidb == 'POSTGIS':
        from glass.geo.gql.prox import st_buffer
    else:
        from glass.geo.gql.prox import splite_buffer as st_buffer
    from glass.dct.geo.torst     import shp_to_rst
    from glass.dct.geo.toshp.cff import shp_to_grs
    
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
            grsVect, int(cls), None, None, "rbb_{}".format(int(cls)), 
            api="grass"
        )
        time_w = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(cls)] = rstVect
        
        timeGasto[tk]   = ('do_buffer_{}'.format(cls), time_y - time_x)
        timeGasto[tk+1] = ('import_{}'.format(cls), time_z - time_y)
        timeGasto[tk+2] = ('torst_{}'.format(cls), time_w - time_z)
        
        tk += 3
    
    return clsRst, timeGasto


def grs_vect_bbuffer(osmdata, lineTbl, api_db='SQLITE'):
    """
    Basic Buffer strategie
    """
    
    import datetime
    from glass.geo.df.prox.bf   import _buffer
    from glass.geo.df.gop.genze import dissolve
    from glass.geo.df.tbl.grs   import add_table
    from glass.sql.prop        import row_num as cnt_row
    from glass.dct.geo.toshp.db  import dbtbl_to_shp as db_to_shp
    
    WHR = "basic_buffer IS NOT NULL"
    
    # Check if we have data
    time_a = datetime.datetime.now().replace(microsecond=0)
    N = cnt_row(osmdata, lineTbl, where=WHR,
        api='psql' if api_db == 'POSTGIS' else 'sqlite'
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    grsVect = db_to_shp(
        osmdata, lineTbl, "geometry", "bb_lnh", where=WHR, filterByReg=True,
        inDB='psql' if api_db == 'POSTGIS' else 'sqlite',
        outShpIsGRASS=True
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    grsBuf  = _buffer(
        grsVect, "bf_basic_buffer", "bb_poly", api="grass", geom_type="line"
    )
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    grsDiss = dissolve(grsBuf, "bb_diss", "basic_buffer", api="grass")
    add_table(grsDiss, None, lyrN=1, asCMD=True)
    time_e = datetime.datetime.now().replace(microsecond=0)
    
    return grsDiss, {
        0 : ('count_rows', time_b - time_a),
        1 : ('import', time_c - time_b),
        2 : ('buffer', time_d - time_c),
        3 : ('dissolve', time_e - time_d)
    }


def num_base_buffer(osmdb, lineTbl, folder, cells, srscode, rtemplate,
                    api='SQLITE'):
    """
    Data from Lines to Polygons
    """
    
    import datetime
    from threading              import Thread
    from glass.dct.sql.fm       import q_to_obj
    if api=='SQLITE':
        from glass.geo.gql.prox import splite_buffer as st_buffer
    else:
        from glass.geo.gql.prox import st_buffer
    from glass.dct.geo.torst     import shp_to_rst
    
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

