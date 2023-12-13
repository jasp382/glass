"""
Rule 1 - Selection
"""

import datetime as dt

from glass.prop.sql import row_num

def grs_rst(db, polyTbl, api='SQLITE'):
    """
    Simple selection, convert result to Raster
    """

    from glass.sql.q     import q_to_obj
    from glass.it.shp    import dbtbl_to_shp as db_to_grs
    from glass.dtt.torst import grsshp_to_grsrst as shp_to_rst
    
    # Get Classes 
    time_a = dt.datetime.now().replace(microsecond=0)
    lulcCls = q_to_obj(db, (
        f"SELECT selection FROM {polyTbl} "
        "WHERE selection IS NOT NULL "
        "GROUP BY selection"
    ), db_api='psql' if api == 'POSTGIS' else 'sqlite').selection.tolist()
    time_b = dt.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Import data into GRASS and convert it to raster
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        time_x = dt.datetime.now().replace(microsecond=0)
        grsVect = db_to_grs(
            db, polyTbl, "geometry", f"rule1_{str(cls)}",
            inDB='psql' if api == 'POSTGIS' else 'sqlite',
            where=f"selection = {str(cls)}", notTable=True,
            filterByReg=True, outShpIsGRASS=True
        )
        time_y = dt.datetime.now().replace(microsecond=0)
        
        grsRst = shp_to_rst(
            grsVect, int(cls), f"rst_rule1_{str(cls)}",
            cmd=True
        )
        time_z = dt.datetime.now().replace(microsecond=0)
        
        clsRst[int(cls)] = grsRst
        timeGasto[tk]    = (f'import_{cls}', time_y - time_x)
        timeGasto[tk+1]  = (f'torst_{cls}', time_z - time_y)
        
        tk += 2
    
    return clsRst, timeGasto


def grs_vector(db, table):
    """
    Simple Selection using GRASS GIS
    """

    from glass.gp.gen   import dissolve
    from glass.tbl.grs  import add_table
    from glass.prop.sql import row_num as cont_row
    from glass.it.shp   import dbtbl_to_shp as db_to_grs
    
    # Check if we have interest data
    time_a = dt.datetime.now().replace(microsecond=0)
    N = cont_row(db, table, where=None, api='psql')
    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows', time_b - time_a)}
    
    # Data to GRASS GIS
    gv = db_to_grs(
        db, table, "geometry", "sel_rule",
        where=None, filterByReg=True,
        inDB='psql', api="grass"
    )
    time_c = dt.datetime.now().replace(microsecond=0)
    
    dissVect = dissolve(gv, "diss_sel_rule", "lulc", api="grass")
    
    add_table(dissVect, None, lyrN=1, asCMD=True)
    time_d = dt.datetime.now().replace(microsecond=0)
    
    return dissVect, {
        0 : ('count_rows', time_b - time_a),
        1 : ('import', time_c - time_b),
        2 : ('dissolve', time_d - time_c)
    }


def num_selection(osmdb, polyTbl, folder,
                  cellsize, srscode, rstTemplate, api='SQLITE'):
    """
    Select and Convert to Raster
    """
    
    import datetime;       import os
    from threading         import Thread
    if api == 'SQLITE':
        from glass.tbl.filter import sel_by_attr
    else:
        from glass.it.shp import dbtbl_to_shp as sel_by_attr
    from glass.sql.q     import q_to_obj
    from glass.dtt.torst   import shp_to_rst
    
    # Get classes in data
    time_a = datetime.datetime.now().replace(microsecond=0)
    classes = q_to_obj(osmdb, (
        f"SELECT selection FROM {polyTbl} "
        "WHERE selection IS NOT NULL "
        "GROUP BY selection"
    ), db_api='psql' if api == 'POSTGIS' else 'sqlite').selection.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Select and Export
    clsRst = {}
    SQL_Q = "SELECT {lc} AS cls, geometry FROM {tbl} WHERE selection={lc}"
    def FilterAndExport(CLS, cnt):
        time_x = datetime.datetime.now().replace(microsecond=0)
        if api == 'SQLITE':
            shp = sel_by_attr(
                osmdb, SQL_Q.format(lc=str(CLS), tbl=polyTbl),
                os.path.join(folder, f'sel_{str(CLS)}.shp'),
                api_gis='ogr'
            )
        else:
            shp = sel_by_attr(
                osmdb, SQL_Q.format(lc=str(CLS), tbl=polyTbl), "geometry",
                os.path.join(folder, f'sel_{str(CLS)}.shp'),
                api='pgsql2shp', tableIsQuery=True
            )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        rstCls = shp_to_rst(
            shp, None, cellsize, 0,
            os.path.join(folder, f'sel_{str(CLS)}.tif'),
            epsg=srscode, rst_template=rstTemplate, api='pygdal'
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(CLS)] = rstCls
        timeGasto[cnt + 1] = (f'toshp_{str(CLS)}', time_y - time_x)
        timeGasto[cnt + 2] = (f'torst_{str(CLS)}', time_z - time_y)
    
    trs = []
    for i in range(len(classes)):
        trs.append(Thread(
            name=f"lll{str(classes[i])}",
            target=FilterAndExport, args=(classes[i], (i+1) * 10)
        ))
    
    for t in trs: t.start()
    for t in trs: t.join()
    
    return clsRst, timeGasto

