"""
Clean Geometries
"""


def fix_geom(db, table, geom, out=None, colsSelect=None, whr=None, 
             method='linework', keepcollapsed=False):
    """
    Remove some topological incorrections on the PostGIS data

    the function attempts to create a valid representation of a given invalid 
    geometry without losing any of the input vertices. Valid geometries are returned 
    unchanged.

    Supported inputs are: POINTS, MULTIPOINTS, LINESTRINGS, MULTILINESTRINGS, 
    POLYGONS, MULTIPOLYGONS and GEOMETRYCOLLECTIONS containing any mix of them.

    In case of full or partial dimensional collapses, the output geometry may 
    be a collection of lower-to-equal dimension geometries, or a geometry of 
    lower dimension.

    Single polygons may become multi-geometries in case of self-intersections.

    The params argument can be used to supply an options string to select the 
    method to use for building valid geometry. The options string is in the 
    format "method=linework|structure keepcollapsed=true|false". If no "params" 
    argument is provided, the "linework" algorithm will be used as the default.

    The "method" key has two values.

    "linework" is the original algorithm, and builds valid geometries by first 
    extracting all lines, noding that linework together, then building a value 
    output from the linework.

    "structure" is an algorithm that distinguishes between interior and 
    exterior rings, building new geometry by unioning exterior rings, and 
    then differencing all interior rings.

    The "keepcollapsed" key is only valid for the "structure" algorithm, and 
    takes a value of "true" or "false". When set to "false", geometry components 
    that collapse to a lower dimensionality, for example a one-point linestring 
    would be dropped. 
    """
    
    from glass.sql.q import q_to_ntbl

    methods = ['linework', "structure"]
    method = method if method in methods else methods[0]
    if method == 'structure':
        keep = ' keepcollapsed=true' if keepcollapsed else \
            'keepcollapsed=false'
    
    else:
        keep = ''
    
    methodstr = f'{method}{keep}'
    
    if not colsSelect:
        from glass.prop.sql import cols_name
        
        cols_tbl = [f'{table}.{x}' for x in cols_name(
            db, table, sanitizeSpecialWords=None
        ) if x != geom]
    
    else:
        from glass.pys  import obj_to_lst
        
        cols_tbl = [f'{table}.{x}' for x in obj_to_lst(colsSelect) if x != geom]
    
    c = ", ".join(cols_tbl)
    w = "" if not whr else f" WHERE {whr}"
    
    q = (
        f"SELECT {c}, "
            f"CASE WHEN ST_IsValid({geom}) THEN {geom} "
            f"ELSE  ST_MakeValid({geom}, '{methodstr}') END "
        f"AS {geom} FROM {table}{w}"
        )
    
    if not out:
        return q
    
    ntbl = q_to_ntbl(db, out, q, api='psql')
    
    return ntbl


def rm_deadend(db, in_tbl, out_tbl):
    """
    Remove deadend
    """
    
    from glass.prop.sql import cols_name, row_num
    from glass.sql.q    import q_to_ntbl
    from glass.sql.tbl  import rename_tbl
    
    # Sanitize In table
    cols = ", ".join([c for c in cols_name(
        db, in_tbl, sanitizeSpecialWords=True, api='psql'
    ) if c != 'geom' and c != 'gid'])
    
    _t = q_to_ntbl(db, "san_geom", (
        f"SELECT gid, {cols}, geom, "
        "ST_AsText(ST_StartPoint(geom)) AS pnt_start, "
        "ST_AsText(ST_EndPoint(geom)) AS pnt_end FROM ("
            f"SELECT gid, {cols}, (ST_Dump(geom)).geom AS geom "
            f"FROM {in_tbl}"
        ") AS foo"
    ))
    
    run_=1
    i = 1
    while run_:
        # Get Table with Points of lines to delete
        delpnt = q_to_ntbl(db, f"del_pnt_{str(i)}", (
            "SELECT ROW_NUMBER() OVER (ORDER BY txtgeom) AS idx, "
            "txtgeom FROM ("
                "SELECT txtgeom, COUNT(txtgeom) AS npnt FROM ("
                    "SELECT pnt_start AS txtgeom "
                    f"FROM {_t} UNION ALL "
                    "SELECT pnt_end AS txtgeom "
                    f"FROM {_t}"
                ") AS tbl GROUP BY txtgeom"
            ") AS delg WHERE npnt=1"
        ))
        
        npnt = row_num(db, delpnt, api='psql')
        
        if not npnt:
            run_ = None
            break
        
        # Get Lines without dead-end
        Q = (
            "SELECT mtbl.* "
            f"FROM {_t} AS mtbl LEFT JOIN {delpnt} AS st_tbl "
            "ON mtbl.pnt_start = st_tbl.txtgeom "
            f"LEFT JOIN {delpnt} AS end_tbl "
            "ON mtbl.pnt_end = end_tbl.txtgeom "
            "WHERE st_tbl.txtgeom IS NULL AND "
            "end_tbl.txtgeom IS NULL"
        )
        
        _t = q_to_ntbl(db, f"rows_{str(i)}", Q)
        
        i += 1
    
    rename_tbl(db, {_t : out_tbl})
    
    return out_tbl

