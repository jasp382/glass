"""
OGR Overlay with SpatialLite
"""

def intersect_point_with_polygon(sqDB, pntTbl, pntGeom,
                                 polyTbl, polyGeom, outTbl,
                                 pntSelect=None, polySelect=None,
                                 pntQuery=None, polyQuery=None,
                                 outTblIsFile=None):
    """
    Intersect Points with Polygons
    
    What TODO with this?
    """
    
    if not pntSelect and not polySelect:
        raise ValueError("You have to select something")
    
    pnt_tq  = pntTbl if not pntQuery else pntQuery
    poly_tq = polyTbl if not polyQuery else polyQuery

    col_pnt = pntSelect if pntSelect else ""
    col_ply = polySelect if polySelect and not pntSelect else \
        ", " + polySelect if polySelect and pntSelect else ""
    
    sql = (
        f"SELECT {col_pnt}{col_ply} FROM {pnt_tq} "
        f"INNER JOIN {poly_tq} ON "
        f"ST_Within({pntTbl}.{pntGeom}, {polyTbl}.{polyGeom})"
    )
    
    if outTblIsFile:
        from glass.dtt.filter import sel_by_attr
        
        sel_by_attr(sqDB, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.sql.q import q_to_ntbl
        
        q_to_ntbl(sqDB, outTbl, sql, api='ogr2ogr')


def disjoint_polygons_rel_points(sqBD, pntTbl, pntGeom,
                                polyTbl, polyGeom, outTbl,
                                polySelect=None,
                                pntQuery=None, polyQuery=None,
                                outTblIsFile=None):
    """
    Get Disjoint relation
    
    What TODO with this?
    """
    
    if not polySelect:
        raise ValueError("Man, select something!")
    

    selcols ="*" if not polySelect else polySelect
    ply_tbl = polyTbl if not polyQuery else polyQuery
    pnt_tbl = pntTbl if not pntQuery else pntQuery,
    
    sql = (
        f"SELECT {selcols} FROM {ply_tbl} WHERE ("
        f"{polyTbl}.{polyGeom} not in ("
            f"SELECT {polyTbl}.{polyGeom} FROM {pnt_tbl} "
            f"INNER JOIN {ply_tbl} ON "
            f"ST_Within({pntTbl}.{pntGeom}, {polyTbl}.{polyGeom})"
        "))"
    )
    
    if outTblIsFile:
        from glass.dtt.filter import sel_by_attr
        
        sel_by_attr(sqBD, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.sql.q import q_to_ntbl
        
        q_to_ntbl(sqBD, outTbl, sql, api='ogr2ogr')

