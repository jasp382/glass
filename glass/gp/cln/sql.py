"""
Clean Geometries
"""


def fix_geom(db, table, geom, out_tbl, colsSelect=None, whr=None):
    """
    Remove some topological incorrections on the PostGIS data
    """
    
    from glass.sql.q import q_to_ntbl
    
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
            f"ELSE  ST_MakeValid({geom}) END "
        f"AS {geom} FROM {table}{w}"
        )
    
    ntbl = q_to_ntbl(db, out_tbl, q, api='psql')
    
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
            "FROM {mtbl} AS mtbl LEFT JOIN {ptbl} AS st_tbl "
            "ON mtbl.pnt_start = st_tbl.txtgeom "
            "LEFT JOIN {ptbl} AS end_tbl "
            "ON mtbl.pnt_end = end_tbl.txtgeom "
            "WHERE st_tbl.txtgeom IS NULL AND "
            "end_tbl.txtgeom IS NULL"
        ).format(cls=cols, mtbl=_t, ptbl=delpnt)
        
        _t = q_to_ntbl(db, f"rows_{str(i)}", Q)
        
        i += 1
    
    rename_tbl(db, {_t : out_tbl})
    
    return out_tbl

