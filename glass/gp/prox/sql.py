"""
Tools for process geographic data on PostGIS
"""


def st_near(db, intbl, ingeom, neartbl, neargeom, output=None,
            near_col='near', api='psql', whrNear=None, outIsFile=None,
            until_dist=None, cols_in_tbl=None, intbl_pk=None,
            cols_near_tbl=None, whr_intbl=None, run_query=None):
    """
    Near tool for PostGIS and Spatialite

    api options:
    * psql
    * splite or spatialite
    """

    from glass.pys   import obj_to_lst
    from glass.sql.q import q_to_obj, q_to_ntbl
    
    if api == 'psql':
        icols = obj_to_lst(cols_in_tbl) if cols_in_tbl else []

        incols = "s.*" if not cols_in_tbl else ", ".join([
            f"s.{c}" for c in icols
        ])
        necols = "" if not cols_near_tbl else ", ".join([
            f"h.{c}" for c in obj_to_lst(cols_near_tbl)
        ])

        if necols != "":
            necols = necols + ", "
        
        whr = f" WHERE {whr_intbl}" if whr_intbl else ""

        q = (
            f"SELECT DISTINCT ON (s.{intbl_pk}) "
            f"{incols}, {necols}"
            "ST_Distance("
                f"s.{ingeom}, h.{neargeom}"
            f") AS {near_col} FROM {intbl} AS s "
            f"LEFT JOIN {neartbl} AS h "
            f"ON ST_DWithin(s.{ingeom}, h.{neargeom}, {str(until_dist)})"
            f"{whr} "
            f"ORDER BY s.{intbl_pk}, ST_Distance(s.{ingeom}, h.{neargeom})"
        ) if intbl_pk and until_dist else (
            f"SELECT {incols}, {necols}"
            f"ST_Distance(m.{ingeom}, j.geom) AS {near_col} "
            f"FROM {intbl} AS s, ("
                f"SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
                f"FROM {neartbl}"
            f") AS h{whr}"
        )

        if output:
            return q_to_ntbl(db, output, q, api='psql')
        
        if run_query:
            if ingeom in icols or not cols_in_tbl:
                _out = q_to_obj(db, q, geomCol=ingeom)
            
            else:
                _out = q_to_obj(db, q, geomCol=None)
            
            return _out

        return q
    
    elif api == 'splite' or api == 'spatialite':
        whr = "" if not whrNear else f" WHERE {whrNear}"
        Q = (
            f"SELECT m.*, ST_Distance(m.{ingeom}, j.geom) AS {near_col} "
            f"FROM {intbl} AS m, ("
                f"SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
                f"FROM {neartbl}{whr}"
            ") AS j"
        )

        if output and outIsFile:
            from glass.dtt.filter import sel_by_attr

            sel_by_attr(db, Q, output, api_gis='ogr')

            return output
        
        elif output and not outIsFile:
            from glass.sql.q import q_to_ntbl

            q_to_ntbl(db, output, Q, api='ogr2ogr')

            return output
        else:
            return Q
    
    else:
        raise ValueError(f"api {api} does not exist!")


def near_cntr_inside_poly(db, poly, pnt, polyid, polygeom, pntgeom,
    otbl=None, poly_cols=None, pnt_cols=None, whrpoly=None):
    """
    Find points inside polygons and id the point
    near the polygon centroid
    """

    from glass.sql.q import q_to_ntbl, q_to_obj

    if not poly_cols and not pnt_cols:
        cols = 'foo.*'
        polycols = 'poly.*'
        pntcols  = 'pnt.*'
    
    else:
        _cols = []

        if poly_cols:
            _cols.extend(list(poly_cols.keys()))

            polycols = ",".join([
                f"{poly_cols[k]} AS {k}" for k in poly_cols
            ])
        
        else:
            polycols = ''
        
        if pnt_cols:
            _cols.extend(list(pnt_cols.keys()))

            pntcols = ", ".join([
                f"{pnt_cols[k]} AS {k}" for k in pnt_cols
            ])

            if polycols:
                pntcols = ", " + pntcols
        
        else:
            pntcols = ''
        
        cols = ", ".join([f"foo.{c}" for c in _cols])

    whrpoly = "" if not whrpoly else f"{whrpoly} AND "

    q = (
        f"SELECT {cols}, "
        f"ROW_NUMBER() OVER(PARTITION BY foo.{polyid} "
            f"ORDER BY foo.{polyid}) AS cpoly "
        "FROM ("
            f"SELECT poly.{polyid}, {polycols}{pntcols}, "
            "ST_Distance("
                f"ST_Centroid(poly.{polygeom}), "
                f"pnt.{pntgeom}) AS dist, "
            f"MIN(ST_Distance(ST_Centroid(poly.{polygeom}), pnt.{pntgeom})) "
                f"OVER(PARTITION BY poly.{polyid} ORDER BY poly.{polyid}) AS mindist "
            f"FROM {poly} AS poly, {pnt} AS pnt "
            f"WHERE {whrpoly}"
            f"ST_Contains(poly.{polygeom}, pnt.{pntgeom}) IS TRUE"
        ") AS foo "
        "WHERE dist = mindist"
    )

    # Dois pontos podem estar a mesma distancia do centroide
    fq = (
        f"SELECT {cols} FROM ({q}) AS foo WHERE foo.cpoly = 1"
    )

    if otbl:
        _out = q_to_ntbl(db, otbl, fq)
    
    else:
        if not poly_cols or polygeom in poly_cols:
            _out = q_to_obj(db, fq, geomCol=polygeom)
        
        else:
            _out = q_to_obj(db, fq)
    
    return _out

