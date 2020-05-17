"""
Rule 1 - Selection
"""

def grs_rst(db, polyTbl, api='SQLITE'):
    """
    Simple selection, convert result to Raster
    """
    
    import datetime as dt
    from glass.sql.q   import q_to_obj
    from glass.it.shp   import dbtbl_to_shp as db_to_grs
    from glass.dp.torst import grsshp_to_grsrst as shp_to_rst
    
    # Get Classes 
    time_a = dt.datetime.now().replace(microsecond=0)
    lulcCls = q_to_obj(db, (
        "SELECT selection FROM {} "
        "WHERE selection IS NOT NULL "
        "GROUP BY selection"
    ).format(polyTbl), db_api='psql' if api == 'POSTGIS' else 'sqlite').selection.tolist()
    time_b = dt.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Import data into GRASS and convert it to raster
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        time_x = dt.datetime.now().replace(microsecond=0)
        grsVect = db_to_grs(
            db, polyTbl, "geometry", "rule1_{}".format(str(cls)),
            inDB='psql' if api == 'POSTGIS' else 'sqlite',
            where="selection = {}".format(str(cls)), notTable=True,
            filterByReg=True, outShpIsGRASS=True
        )
        time_y = dt.datetime.now().replace(microsecond=0)
        
        grsRst = shp_to_rst(
            grsVect, int(cls), f"rst_rule1_{str(cls)}",
            cmd=True
        )
        time_z = dt.datetime.now().replace(microsecond=0)
        
        clsRst[int(cls)] = grsRst
        timeGasto[tk]    = ('import_{}'.format(cls), time_y - time_x)
        timeGasto[tk+1]  = ('torst_{}'.format(cls), time_z - time_y)
        
        tk += 2
    
    return clsRst, timeGasto


def grs_vector(db, polyTable, apidb='SQLITE'):
    """
    Simple Selection using GRASS GIS
    """
    
    import datetime
    from glass.gp.gen    import dissolve
    from glass.tbl.grs   import add_table
    from glass.prop.sqlport row_num as cont_row
    from glass.it.shp    import dbtbl_to_shp as db_to_grs
    
    WHR = "selection IS NOT NULL"
    
    # Check if we have interest data
    time_a = datetime.datetime.now().replace(microsecond=0)
    N = cont_row(db, polyTable, where=WHR,
        api='psql' if apidb == 'POSTGIS' else 'sqlite'
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows', time_b - time_a)}
    
    # Data to GRASS GIS
    grsVect = db_to_grs(
        db, polyTable, "geometry", "sel_rule",
        where=WHR, filterByReg=True,
        inDB='psql' if apidb == 'POSTGIS' else 'sqlite',
        outShpIsGRASS=True
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    dissVect = dissolve(
        grsVect, "diss_sel_rule", "selection", api="grass")
    
    add_table(dissVect, None, lyrN=1, asCMD=True)
    time_d = datetime.datetime.now().replace(microsecond=0)
    
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
    from glass.dp.torst   import shp_to_rst
    
    # Get classes in data
    time_a = datetime.datetime.now().replace(microsecond=0)
    classes = q_to_obj(osmdb, (
        "SELECT selection FROM {} "
        "WHERE selection IS NOT NULL "
        "GROUP BY selection"
    ).format(
        polyTbl
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
                os.path.join(folder, 'sel_{}.shp'.format(str(CLS))),
                api_gis='ogr'
            )
        else:
            shp = sel_by_attr(
                osmdb, SQL_Q.format(lc=str(CLS), tbl=polyTbl), "geometry",
                os.path.join(folder, 'sel_{}.shp'.format(str(CLS))),
                api='pgsql2shp', tableIsQuery=True
            )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        rstCls = shp_to_rst(
            shp, None, cellsize, 0,
            os.path.join(folder, 'sel_{}.tif'.format(str(CLS))),
            epsg=srscode, rst_template=rstTemplate, api='gdal'
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(CLS)] = rstCls
        timeGasto[cnt + 1] = ('toshp_{}'.format(str(CLS)), time_y - time_x)
        timeGasto[cnt + 2] = ('torst_{}'.format(str(CLS)), time_z - time_y)
    
    trs = []
    for i in range(len(classes)):
        trs.append(Thread(
            name="lll{}".format(str(classes[i])),
            target=FilterAndExport, args=(classes[i], (i+1) * 10)
        ))
    
    for t in trs: t.start()
    for t in trs: t.join()
    
    return clsRst, timeGasto

