"""
Overlay operations using SQL
"""

from glass.prop.sql import cols_name
from glass.pys      import obj_to_lst
from glass.sql.q    import q_to_ntbl, exec_write_q


def feat_within(db, left_tbl, left_geom, within_tbl, within_geom, out=None,
    left_cols=None, within_cols=None, outTblIsFile=None,
    geom_col='left', join='INNER', outlyr=None, geomname='geometry'):
    """
    Get Features within other Geometries in withinTbl
    e.g. Intersect points with Polygons
    
    apiToUse options:
    * sqlite;
    * psql.
    """
    
    from glass.pys import obj_to_lst

    join = "INNER" if join != 'INNER' and join != 'LEFT' \
        and join != 'RIGHT' and join != 'OUTER' else join
    
    lcols = None if not left_cols else ", ".join([
        f"itbl.{c}" for c in obj_to_lst(left_cols)
    ])

    wcols = None if not within_cols else ", ".join([
        f"wtbl.{c}" for c in obj_to_lst(within_cols)
    ])

    geom_col = f"itbl.{left_geom}" if geom_col == 'left' else \
        f"wtbl.{within_geom}" if geom_col == 'within' \
            else f"itbl.{left_geom}"
    
    geoname = 'geometry' if not geomname else geomname
    
    if not lcols and not wcols:
        csel = "itbl.*, wtbl.*"
    
    elif lcols and not wcols:
        csel = lcols
        
    elif not lcols and wcols:
        csel = wcols
        
    else:
        csel = f"{lcols}, {wcols}"
    
    q = (
        f"SELECT {csel}, {geom_col} AS {geoname} "
        f"FROM {left_tbl} AS itbl "
        f"{join} JOIN {within_tbl} AS wtbl ON "
        f"ST_Within(itbl.{left_geom}, wtbl.{within_geom})"
    )

    if out and not outTblIsFile:
        q_to_ntbl(db, out, q, api="ogr2ogr")

        return out
    
    elif out and outTblIsFile:
        from glass.it.shp import dbtbl_to_shp

        dbtbl_to_shp(
            db, q, geoname, out, api="ogr2ogr",
            tableIsQuery=True, olyr=outlyr
        )

        return out
    
    else:
        return q


def feat_not_within(db, inTbl, inGeom, withinTbl, withinGeom, outTbl,
                    inTblCols=None, outTblIsFile=None,
                    apiToUse='OGR_SPATIALITE', geom_col=None):
    """
    Get features not Within with any of the features in withinTbl
    
    apiToUse options:
    * OGR_SPATIALITE;
    * POSTGIS.
    """
    
    

    selcols = "*" if not inTblCols else ", ".join(obj_to_lst(inTblCols))
    
    Q = (
        f"SELECT {selcols} FROM {inTbl} AS in_tbl WHERE ("
        f"in_tbl.{inGeom} NOT IN ("
            f"SELECT inin_tbl.{inGeom} FROM {withinTbl} AS wi_tbl "
            f"INNER JOIN {inTbl} AS inin_tbl ON "
            f"ST_Within(wi_tbl.{withinGeom}, inin_tbl.{inGeom})"
        "))"
    )
    
    if apiToUse == "OGR_SPATIALITE":
        if outTblIsFile:
            from glass.dtt.filter import sel_by_attr
            
            sel_by_attr(db, Q, outTbl, api_gis='ogr')
        
        else:
            from glass.sql.q import q_to_ntbl
            
            q_to_ntbl(db, outTbl, Q, api='ogr2ogr')
    
    elif apiToUse == "POSTGIS":
        if outTblIsFile:
            if not geom_col:
                raise ValueError((
                    "To export a PostGIS table to file, "
                    "geom_col must be specified"
                ))

            from glass.it.shp import dbtbl_to_shp
            
            dbtbl_to_shp(
                db, Q, geom_col, outTbl, api='pgsql2shp',
                tableIsQuery=True
            )
        
        else:
            q_to_ntbl(db, outTbl, Q, api='psql')
    
    else:
        raise ValueError((
            f"API {apiToUse} is not available. OGR_SPATIALITE and POSTGIS "
            "are the only valid options"
        ))
    
    return outTbl


def intersect_in_same_table(db_name, table, geomA, geomB, outtable,
                            intersectField='intersects',
                            intersectGeom=None, colsSel=None):
    """
    Intersect two Geometries in the same table
    """
    
    from glass.pys import obj_to_lst
    
    cols = obj_to_lst(colsSel)
    csel = "*" if not cols else ", ".join(cols)

    intgeom= "" if not intersectGeom else \
        f", ST_Intersection({geomA}, {geomB}) AS intersect_geom "
    
    intgeomcol = "" if not intersectGeom else ", intersect_geom "
    
    return q_to_ntbl(db_name, outtable, (
        f"SELECT {csel}, CASE "
            "WHEN interse IS TRUE "
            "THEN 1 ELSE 0 "
        f"END AS {intersectField} "
         f"{intgeomcol}FROM ("
            f"SELECT {csel}, ST_Intersects({geomA}, {geomB}) AS interse "
            f"{intgeom}FROM {table}"
         ") AS tst"
    ), api='psql')


def line_intersection_pnt(db, inTbl, outTbl):
    """
    Get Points where two line features of the same feature class
    intersects.
    """
    
    # Get Points representing intersection
    Q_a = (
        "SELECT foo.gid, "
        "ST_Intersection(foo.geom, foo2.tstgeom) AS geom "
        "FROM (SELECT gid, geom FROM {t}) AS foo, ("
            "SELECT gid AS tstfid, geom AS tstgeom "
            f"FROM {inTbl}"
        ") AS foo2 "
        "WHERE foo.gid <> foo2.tstfid AND "
        "ST_Intersects(foo.geom, foo2.tstgeom)"
    )
    
    Q_b = (
        "SELECT gid AS ogid, (ST_Dump(geom)).geom AS geom FROM ("
            "SELECT gid, "
            "CASE "
                "WHEN ST_GeometryType(geom) = 'ST_LineString' "
                "THEN ST_Collect(ST_StartPoint(geom), ST_EndPoint(geom)) "
                "ELSE geom "
            "END AS geom FROM ("
                "SELECT gid, (ST_Dump(geom)).geom AS geom "
                f"FROM ({Q_a}) AS ttbl"
            ") AS tbl"
        ") AS tbll"
    )
    
    allpnt = q_to_ntbl(db, "all_pnt", Q_b)
    
    Q_main = (
        "SELECT ogid, (ogid - 1) AS ofid, geom FROM ("
            "SELECT mtbl.*, st_tbl.st_pnt, st_tbl.end_pnt, "
            "CASE "
                "WHEN mtbl.geom = st_tbl.st_pnt "
                "THEN 1 ELSE 0 "
            "END AS is_start, "
            "CASE "
                "WHEN mtbl.geom = st_tbl.end_pnt "
                "THEN 1 ELSE 0 "
            "END AS is_end "
            f"FROM {allpnt} AS mtbl INNER JOIN ("
                "SELECT gid, ST_StartPoint(geom) AS st_pnt, "
                "ST_EndPoint(geom) AS end_pnt FROM ("
                    "SELECT gid, (ST_Dump(geom)).geom AS geom "
                    f"FROM {inTbl}"
                ") AS foo"
            ") AS st_tbl "
            "ON mtbl.ogid = st_tbl.gid"
        ") AS foo WHERE is_start = 0 AND is_end = 0"
    )
    
    return q_to_ntbl(db, outTbl, Q_main)


def del_topoerror_shps(db, shps, epsg, outfolder):
    """
    Remove topological errors from Feature Class data using PostGIS
    """
    
    import os
    from glass.pys      import obj_to_lst
    from glass.prop.sql import cols_name
    from glass.it.db    import shp_to_psql
    from glass.it.shp   import dbtbl_to_shp
    
    shps = obj_to_lst(shps)
    
    TABLES = shp_to_psql(db, shps, srs=epsg, api="ogr2ogr")
    
    NTABLE = [q_to_ntbl(
        db, "nt_{}".format(t),
        "SELECT {cols}, ST_MakeValid({tbl}.geom) AS geom FROM {tbl}".format(
            cols = ", ".join([f"{TABLES[t]}.{x}" for x in cols_name(
                db, TABLES[t], sanitizeSpecialWords=None
            ) if x != 'geom']),
            tbl=TABLES[t]
        ), api='psql'
    ) for t in range(len(TABLES))]
    
    for t in range(len(NTABLE)):
        dbtbl_to_shp(db, NTABLE[t], "geom", os.path.join(
            outfolder, TABLES[t]), tableIsQuery=None, api='pgsql2shp')


def st_pgintersection(db, atbl, btbl, apk, lgeom, rgeom, primitive, output=None,
                 new_pk='fid_pk', new_geom='geom',
                 aselcols=None, bselcols=None, outisfile=None, olyr=None):
    """
    Intersect two layers

    primitive is the geometric primitive (point, line, polygons)

    priority is an indication of the fields that the user wants to include in
    the output - fields of aShp or fields of bShp.
    The user could giver a list (with fields for selection) as value for the
    priority argument.
    """

    _acols = obj_to_lst(aselcols) if aselcols else \
        cols_name(db, atbl, api='psql')
    _bcols = obj_to_lst(bselcols) if bselcols else \
        cols_name(db, btbl, api='psql')
    
    bcols_ = {c : c if c not in _acols and c != apk and c != lgeom else f"{c}_y" for c in _bcols}
    
    acols = ", ".join([f"tbla.{x}" for x in _acols if x != lgeom and x != apk])
    bcols = ", ".join([f"tblb.{y} AS {bcols_[y]}" for y in bcols_ if y != rgeom])

    if primitive == 'point':

        q = (
            f"SELECT ROW_NUMBER() OVER(ORDER BY tbla.{apk}) AS {new_pk}, "
            f"tbla.{apk} AS {apk if apk != new_pk else f'{apk}_1'}, "
            f"{acols}, {bcols}, {lgeom} AS {new_geom} "
            f"FROM {atbl} AS tbla "
            f"INNER JOIN {btbl} AS tblb "
            f"ON ST_Within(tbla.{lgeom}, tblb.{rgeom})"
        )
        

    elif primitive == 'line':

        q = (
            f"SELECT ROW_NUMBER() OVER(ORDER BY {apk}) AS {new_pk}, * "
            "FROM ("
                f"SELECT tbla.{apk}, {acols}, {bcols}, "
                f"(ST_DUMP(ST_Intersection("
                    f"tblb.{rgeom}, tbla.{lgeom}))).geom AS {new_geom} "
                f"FROM {btbl} AS tblb "
                f"INNER JOIN {atbl} AS tbla "
                f"ON ST_Intersects(tblb.{rgeom}, "
                f"tbla.{lgeom})"
            f") As foo "
            f"WHERE ST_Dimension(foo.{new_geom}) = 1;"
        )

    elif primitive == 'polygon':

        q = (
            f'SELECT ROW_NUMBER() OVER(ORDER BY tbla.{apk}) AS {new_pk}, '
            f'tbla.{apk} AS {apk if apk != new_pk else f"{apk}_1"}, {acols}, {bcols}, '
            'ST_Multi(ST_Buffer(ST_Intersection('
                f'tbla.{lgeom}, tblb.{rgeom}'
            f'), 0.0)) As {new_geom} '
            f'FROM {atbl} AS tbla '
            f'INNER JOIN {btbl} AS tblb '
            f'ON ST_Intersects(tbla.{lgeom}, tblb.{rgeom}) '
            'WHERE Not ST_IsEmpty(ST_Buffer(ST_Intersection('
                f'tbla.{lgeom}, tblb.{rgeom}'
            '), 0.0))'
        )
    
    if output and not outisfile:
        ntbl = q_to_ntbl(db, output, q, api='psql')

        exec_write_q(db, [(
            f"ALTER TABLE {ntbl} ADD CONSTRAINT "
            f"{ntbl}_pk PRIMARY KEY ({new_pk})"
        ), (
            f"CREATE INDEX {ntbl}_geom_idx ON "
            f"{ntbl} USING gist ({new_geom})"
        )], api='psql')

        return output
    
    elif output and outisfile:
        from glass.it.shp import dbtbl_to_shp

        dbtbl_to_shp(
            db, q, new_geom, output,
            api='ogr2ogr', tableIsQuery=True,
            olyr=olyr
        )

        return output
    
    else:
        return q


def check_autofc_overlap(checkShp, epsg, dbname, outOverlaps):
    """
    Check if the features of one Feature Class overlaps each other
    """
    
    import os
    from glass.sql.db import create_pgdb
    from glass.it.db  import shp_to_psql
    from glass.it.shp import dbtbl_to_shp
    
    create_pgdb(dbname)
    
    # Send data to postgresql
    table = shp_to_psql(dbname, checkShp, srs=epsg, api="pandas")
    
    # Produce result
    q = (
        "SELECT foo.* FROM ("
            f"SELECT * FROM {table}"
        ") AS foo, ("
            f"SELECT cat AS relcat, geom AS tst_geom FROM {table}"
        ") AS foo2 "
        "WHERE ("
            "ST_Overlaps(geom, tst_geom) IS TRUE OR "
            "ST_Equals(geom, tst_geom) IS TRUE OR "
            "ST_Contains(geom, tst_geom) IS TRUE"
        ") AND cat <> relcat"
    )
    
    resultTable = os.path.splitext(os.path.basename(outOverlaps))[0]
    q_to_ntbl(dbname, resultTable, q, api='psql')
    
    dbtbl_to_shp(
        dbname, resultTable, "geom",
        outOverlaps, api='psql', epsg=epsg
    )
    
    return outOverlaps


def st_erase(db, itbl, erase_tbl, igeom, erase_geom, otbl=None, method=1):
    """
    Erase
    """
    
    from glass.prop.sql import cols_name
    
    cols = ", ".join([f"tbla.{x}" for x in cols_name(
        db, itbl, api='psql'
    ) if x != igeom])

    method = 1 if method != 2 and method != 3 else method

    if method == 1:
        mq = (
            f"SELECT {cols}, "
            "CASE "
    	        f"WHEN tblb.{erase_geom} IS NOT NULL THEN "
    	        f"ST_Difference(tbla.{igeom}, tblb.{erase_geom}) "
    	        f"ELSE tbla.{igeom} "
            f"END AS {igeom} "
            f"FROM {itbl} AS tbla "
            f"LEFT JOIN {erase_tbl} AS tblb "
            f"ON ST_Intersects(tbla.{igeom}, tblb.{erase_geom})"
        )

        q = (
            f"SELECT {cols}, "
            f"(ST_Dump(ST_UnaryUnion(ST_Collect({igeom})))).geom AS {igeom} "
            f"FROM ({mq}) AS tbla "
            f"GROUP BY {cols}"
        )
    
    elif method == 2:
        q = (
            f"SELECT {cols}, "
            f"ST_Difference(tbla.{igeom}, tblb.{erase_geom}) AS {igeom} "
            f"FROM {itbl} AS tbla, ("
                f"SELECT ST_UnaryUnion(ST_Collect({erase_geom})) AS {erase_geom} "
                f"FROM {erase_tbl}"
            ") AS tblb "
        )
    
    elif method == 3:
        q = (
            f"SELECT {cols}, "
            f"ST_Difference(tbla.{igeom}, tblb.{erase_geom}) AS {igeom} "
            f"FROM {itbl} AS tbla, ("
                f"SELECT ST_UnaryUnion(ST_Collect(mtbl.{erase_geom})) AS {erase_geom} "
                f"FROM {erase_tbl} AS mtbl "
                f"INNER JOIN {itbl} AS jtbl "
                f"ON ST_Intersects(mtbl.{erase_geom}, jtbl.{igeom})"
            ") AS tblb"
        )
    
    if otbl:
        return q_to_ntbl(db, otbl, q, api='psql')
    
    return q


def st_erase_opt(db, itbl, ipk, erase_tbl, igeom, erase_geom, otbl=None):
    """
    Optimize ST_Difference with ST_Subdivide result
    """

    cols = ", ".join([f"tbla.{x}" for x in cols_name(
        db, itbl, api='psql'
    ) if x != igeom and x != ipk])

    valopk, opk, nk = None, '', 0
    while not valopk:
        opk = f"prev_{ipk}" if not nk else f"prev_{ipk}_{str(nk)}"

        if opk not in cols:
            valopk = True

        nk += 1

    q = (
        f"SELECT ROW_NUMBER() OVER(ORDER BY {ipk}) AS {ipk}, "
        f"tbla.{ipk} AS {opk}, {cols}, "
        f"(ST_Dump(ST_UnaryUnion(ST_Collect({igeom})))).geom AS {igeom} "
        "FROM ("
            f"SELECT tbla.{ipk}, {cols}, "
            "CASE "
	            f"WHEN tblb.{ipk} IS NOT NULL THEN "
	            f"ST_Difference(tbla.{igeom}, tblb.{erase_geom}) "
	            f"ELSE tbla.{igeom} " 
            f"END AS {igeom} "
            f"FROM {itbl} AS tbla "
            "LEFT JOIN ("
	            f"SELECT DISTINCT j.{ipk}, r.{erase_geom} "
	            f"FROM {erase_tbl} AS r "
	            f"INNER JOIN {itbl} AS j "
	            f"ON ST_Intersects(r.{erase_geom}, j.{igeom})"
            ") AS tblb "
            f"ON tbla.{ipk} = tblb.{ipk}"
        ") AS tbla "
        f"GROUP BY tbla.{ipk}, {cols}"
    )

    if otbl:
        return q_to_ntbl(db, otbl, q, api='psql')

    return q


def st_pgerase(db, itbl, ipk, erase_tbl, igeom, egeom, otbl=None, selcols=None):
    """
    Erase tool implemented in PostgreSQL/PostGIS
    """

    # Get columns to be selected
    clst = obj_to_lst(selcols) if selcols else \
        cols_name(db, itbl, api='psql')
    
    cols = ", ".join([f"tbla.{x}" for x in clst if x != igeom and x != ipk])

    valopk, opk, nk = None, '', 0
    while not valopk:
        opk = f"ori_{ipk}" if not nk else f"ori_{ipk}_{str(nk)}"

        if opk not in cols:
            valopk = True
        
        nk += 1

    q = (
        f"SELECT ROW_NUMBER() OVER(ORDER BY tbla.{ipk}) AS {ipk}, "
        f"tbla.{ipk} AS {opk}, {cols}, {igeom} "
        "FROM ("
            f"SELECT tbla.{ipk}, {cols}, "
            f"(ST_Dump(tbla.{igeom})).geom AS {igeom} "
            "FROM ("
                f"SELECT tbla.{ipk}, {cols}, "
                "CASE "
                    f"WHEN tblb.{ipk} IS NOT NULL THEN "
                    f"ST_Difference(tbla.{igeom}, tblb.{egeom}) "
                    f"ELSE tbla.{igeom} "
                f"END AS {igeom} "
                f"FROM {itbl} AS tbla "
                "LEFT JOIN ("
                    f"SELECT j.{ipk}, "
                    f"ST_UnaryUnion(ST_Collect(r.{egeom})) AS {egeom} "
                    f"FROM {erase_tbl} AS r "
                    f"INNER JOIN {itbl} AS j "
                    f"ON ST_Intersects(r.{egeom}, j.{igeom}) "
                    f"GROUP BY j.{ipk}"
                ") AS tblb "
                f"ON tbla.{ipk} = tblb.{ipk}"
            ") AS tbla"
        ") AS tbla"
    )

    if otbl:
        ntbl = q_to_ntbl(db, otbl, q, api='psql')

        exec_write_q(db, [(
            f"ALTER TABLE {ntbl} ADD CONSTRAINT "
            f"{ntbl}_pk PRIMARY KEY ({ipk})"
        ), (
            f"CREATE INDEX {ntbl}_geom_idx ON "
            f"{ntbl} USING gist ({igeom})"
        )], api='psql')

        return otbl
    
    return q


def st_touching(db, atbl, ageom, btbl, bgeom, otbl=None, acols=None, bcols=None,
                awhr=None, bwhr=None):
    """
    Get lines where two polygons touches
    """

    _acols = obj_to_lst(acols) if acols else cols_name(db, atbl, api='psql')
    _bcols = obj_to_lst(bcols) if bcols else cols_name(db, btbl, api='psql')
    
    acstr = ", ".join([f"t.{x}" for x in _acols if x != ageom])
    bcstr = ", ".join([f"j.{y}" for y in _bcols if y != bgeom])

    _atbl = f"{atbl} AS t" if not awhr else (
        f"(SELECT * FROM {atbl} WHERE {awhr}) AS t"
    )

    _btbl = f"{btbl} AS j" if not bwhr else (
        f"(SELECT * FROM {btbl} WHERE {bwhr}) AS j"
    )

    q = (
        f"SELECT {acstr}, {bcstr}, "
        f"ST_Intersection(t.{ageom}, j.{bgeom}) AS {ageom} "
        f"FROM {_atbl} "
        f"LEFT JOIN {_btbl} "
        f"ON ST_Touches(t.{ageom}, j.{bgeom}) "
        f"WHERE ST_Intersection(t.{ageom}, j.{bgeom}) IS NOT NULL"
    )

    if otbl:
        ntbl = q_to_ntbl(db, otbl, q, api='psql')

        return ntbl

    return q



def points_in_polygons(db, pnt, pnt_geom, poly, poly_attr, poly_geom,
    outtbl=None, pnt_whr=None, pntattr=None):
    """
    Return polygons containing each point
    """

    from glass.pys   import obj_to_lst
    from glass.sql.q import q_to_obj, q_to_ntbl

    icols = obj_to_lst(pntattr) if pntattr else []
    pntcols = "pnt.*" if not pntattr else ", ".join([
        f"pnt.{c}" for c in icols
    ])

    polycols = ", ".join([f"poly.{c}" for c in obj_to_lst(poly_attr)])

    whr = f" AND {pnt_whr}"

    q = (
        f"SELECT {pntcols}, {polycols} "
        f"FROM {pnt} AS pnt, {poly} AS poly "
        f"WHERE ST_Contains({poly_geom}, {pnt_geom}) IS TRUE{whr}"
    )

    if outtbl:
        _out = q_to_ntbl(db, outtbl, q)
    
    else:
        if pnt_geom in icols or not pntattr:
            _out = q_to_obj(db, q, geomCol=pnt_geom)
        else:
            _out = q_to_obj(db, q, geomCol=None)
    
    return _out



def st_pgleft_union(db, left_tbl, right_tbl, lpk, lgeom, rgeom, out=None, left_cols=None):
    """
    Intersect left table with right table

    Return intersection results
    Return left geometries were there are no intersection

    Intersection + Erase
    """

    left_cols = obj_to_lst(left_cols) if left_cols else \
        cols_name(db, left_tbl, api='psql')
    
    lcols = [x for x in left_cols if x != lgeom and x != lpk]

    strcols = ", ".join(lcols)
    

    # Query intersection
    qint = st_pgintersection(
        db, left_tbl, right_tbl, lpk,
        lgeom, rgeom, 'polygon', new_geom=lgeom,
        aselcols=lcols
    )

    # Query erase
    qerase = st_pgerase(
        db, left_tbl, lpk, right_tbl,
        lgeom, rgeom, selcols=lcols
    )

    # Final query
    q = (
        f"SELECT ROW_NUMBER() OVER(ORDER BY {lpk}) AS {lpk}, "
        f"{lpk} AS {lpk}_0, {strcols}, {lgeom} FROM ("
            f"SELECT {lpk}, {strcols}, {lgeom} "
            f"FROM ({qerase}) AS foo "
            "UNION ALL "
            f"SELECT {lpk}, {strcols}, {lgeom} "
            f"FROM ({qint}) AS tst"
        ") AS fq"
    )

    if out:
        ntbl = q_to_ntbl(db, out, q, api='psql')

        exec_write_q(db, [(
            f"ALTER TABLE {ntbl} ADD CONSTRAINT "
            f"{ntbl}_pk PRIMARY KEY ({lpk})"
        ), (
            f"CREATE INDEX {ntbl}_geom_idx ON "
            f"{ntbl} USING gist ({lgeom})"
        )], api='psql')

        return ntbl
    
    return q

