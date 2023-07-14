"""
Rule 3 and 4 - Area upper than and less than
"""

import datetime as dt

from glass.prop.sql import row_num


def rst_area(db, polygonTable, UPPER=True, api='SQLITE'):
    """
    Select features with area upper than.
    
    A field with threshold is needed in the database.
    """
    
    from glass.sql.q        import q_to_obj
    from glass.it.shp       import dbtbl_to_shp as db_to_grs
    from glass.dtt.torst    import grsshp_to_grsrst as shp_to_rst
    from glass.ete.osm2lulc import GEOM_AREA
    
    RULE_COL = 'area_upper' if UPPER else 'area_lower'
    OPERATOR = " > " if UPPER else " < "
    
    WHR = "{ga} {op} t_{r} AND {r}={cls_}"
    
    # Get Classes
    time_a = dt.datetime.now().replace(microsecond=0)
    lulcCls = q_to_obj(db, (
        f"SELECT {RULE_COL} "
        f"FROM {polygonTable} "
        f"WHERE {GEOM_AREA} {OPERATOR} t_{RULE_COL} "
        f"GROUP BY {RULE_COL}"
    ), db_api='psql' if api == 'POSTGIS' else 'sqlite')[RULE_COL].tolist()
    time_b = dt.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Import data into GRASS and convert it to raster
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        time_x = dt.datetime.now().replace(microsecond=0)
        grsVect = db_to_grs(
            db, polygonTable, "geometry",
            f"{RULE_COL}_{cls}",
            inDB="psql" if api == 'POSTGIS' else 'sqlite',
            where=WHR.format(
                op=OPERATOR, r=RULE_COL, ga=GEOM_AREA, cls_=cls
            ), notTable=True, filterByReg=True, outShpIsGRASS=True
        )
        time_y = dt.datetime.now().replace(microsecond=0)
        timeGasto[tk] = ('import_{}'.format(cls), time_y - time_x)
        
        grsRst = shp_to_rst(
            grsVect, int(cls), f"rst_{RULE_COL}",
            cmd=True
        )
        time_z = dt.datetime.now().replace(microsecond=0)
        timeGasto[tk+1] = ('torst_{}'.format(cls), time_z - time_y)
        
        clsRst[int(cls)] = grsRst
        tk += 2
        
    return clsRst, timeGasto


def grs_vect_selbyarea(osmdb, polyTbl, UPPER=True):
    """
    Select features with area upper than.
    
    A field with threshold is needed in the database.
    """
    
    from glass.gp.gen       import dissolve
    from glass.tbl.grs      import add_table
    from glass.ete.osm2lulc import GEOM_AREA
    from glass.prop.sql     import row_num as cnt_row
    from glass.it.shp       import dbtbl_to_shp as db_to_shp
    
    o = ">" if UPPER else "<"
    d = "upper" if UPPER else "lower"
    
    WHR = f"{GEOM_AREA} {o} t_area_{d} and area_{d} IS NOT NULL"
    
    # Check if we have interest data
    time_a = dt.datetime.now().replace(microsecond=0)
    N = cnt_row(osmdb, polyTbl, where=WHR, api='psql')
    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows', time_b - time_a)}
    
    # Data to GRASS GIS
    grsVect = db_to_shp(
        osmdb, polyTbl, "geometry",
        f"area_{d}", where=WHR, inDB='psql',
        filterByReg=True, outShpIsGRASS=True
    )
    time_c = dt.datetime.now().replace(microsecond=0)
    
    dissVect = dissolve(
        grsVect, f"diss_area_{d}",
        f"area_{d}", api="grass"
    )
    
    add_table(dissVect, None, lyrN=1, asCMD=True)
    time_d = dt.datetime.now().replace(microsecond=0)
    
    return dissVect, {
        0 : ('count_rows', time_b - time_a),
        1 : ('import', time_c - time_b),
        2 : ('dissolve', time_d - time_c)
    }


def num_selbyarea(db, polyTbl, folder, cellsize, srscode, rstTemplate,
                  UPPER=True, api='SQLITE'):
    """
    Select features with area upper than.
    
    A field with threshold is needed in the database.
    """
    
    import os
    from threading          import Thread
    from glass.sql.q     import q_to_obj
    if api == 'SQLITE':
        from glass.tbl.filter import sel_by_attr
    else:
        from glass.it.shp import dbtbl_to_shp as sel_by_attr
    from glass.dtt.torst   import shp_to_rst
    from glass.ete.osm2lulc import GEOM_AREA
    
    # Get OSM Features to be selected for this rule
    RULE_COL = 'area_upper' if UPPER else 'area_lower'
    OPERATOR = " > " if UPPER else " < "
    WHR = "{ga} {op} t_{r} AND {r}={cls_}"
    
    # Get Classes
    time_a = dt.datetime.now().replace(microsecond=0)
    lulcCls = q_to_obj(db, (
        "SELECT {r} FROM {tbl} WHERE {ga} {op} t_{r} GROUP BY {r}"
    ).format(
        r=RULE_COL, tbl=polyTbl, ga=GEOM_AREA, op=OPERATOR
    ), db_api='psql' if api == 'POSTGIS' else 'sqlite')[RULE_COL].tolist()
    time_b = dt.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    clsRst = {}
    SQL_Q = (
        "SELECT geometry, {c} AS cls FROM {tbl} WHERE {w}"
    )
    def selAndExport(CLS, cnt):
        time_x = dt.datetime.now().replace(microsecond=0)
        if api == "SQLITE":
            shpCls = sel_by_attr(
                db, SQL_Q.format(c=str(CLS), tbl=polyTbl, w=WHR.format(
                    op=OPERATOR, r=RULE_COL, ga=GEOM_AREA, cls_=CLS
                )),
                os.path.join(folder, "{}_{}.shp".format(RULE_COL,CLS)),
                api_gis='ogr'
            )
        else:
            shpCls = sel_by_attr(
                db, SQL_Q.format(c=str(CLS), tbl=polyTbl, w=WHR.format(
                    op=OPERATOR, r=RULE_COL, ga=GEOM_AREA, cls_=CLS
                )), "geometry", os.path.join(
                    folder, "{}_{}.shp".format(RULE_COL, str(CLS))
                ), api='pgsql2shp', tableIsQuery=True
            )
        time_y = dt.datetime.now().replace(microsecond=0)
        
        rst = shp_to_rst(
            shpCls, None, cellsize, 0, os.path.join(
                folder, "{}_{}.tif".format(RULE_COL, CLS)
            ), epsg=srscode, rst_template=rstTemplate, api='gdal'
        )
        time_z = dt.datetime.now().replace(microsecond=0)
        
        clsRst[int(CLS)] = rst
        timeGasto[cnt + 1] = ('sq_to_shp_{}'.format(str(CLS)), time_y - time_x)
        timeGasto[cnt + 2] = ('shp_to_rst_{}'.format(str(CLS)), time_z - time_y)
    
    thrds = [Thread(
        name="area-tk{}".format(lulcCls[i]), target=selAndExport,
        args=(lulcCls[i], (i+1) * 10)
    ) for i in range(len(lulcCls))]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    return clsRst, timeGasto


def sel_by_dist_to_pop():
    """
    The assign of OSM Features to the 3 or 14 LULC Class depends one the
    distance to the population 
    """
    
    # For POPULATION DATASET or Residential Building Dataset:
    # To Point | Focal Statistic | Select areas > than threshold |
    # Distance to these areas | Assign classes based on the distance relation
    
    # Other option is:
    # Check if inside the polygons are things normaly within green urban spaces
    # parques infantis, etc.
    
    return None

