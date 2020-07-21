"""
Overlay operations using SQL
"""


def feat_within(db, inTbl, inGeom, withinTbl, withinGeom, outTbl,
    inTblCols=None, withinCols=None, outTblIsFile=None,
    apiToUse='OGR_SPATIALITE', geom_col=None):
    """
    Get Features within other Geometries in withinTbl
    e.g. Intersect points with Polygons
    
    apiToUse options:
    * OGR_SPATIALITE;
    * POSTGIS.
    """
    
    from glass.pyt import obj_to_lst
    
    if not inTblCols and not withinCols:
        colSelect = "intbl.*, witbl.*"
    else:
        if inTblCols and not withinCols:
            colSelect = ", ".join([
                "intbl.{}".format(c) for c in obj_to_lst(inTblCols)
            ])
        
        elif not inTblCols and withinCols:
            colSelect = ", ".join([
                "witbl.{}".format(c) for c in obj_to_lst(withinCols)
            ])
        
        else:
            colSelect = "{}, {}".format(
                ", ".join(["intbl.{}".format(c) for c in obj_to_lst(inTblCols)]),
                ", ".join(["witbl.{}".format(c) for c in obj_to_lst(withinCols)])
            )
    
    Q = (
        "SELECT {selcols} FROM {in_tbl} AS intbl "
        "INNER JOIN {within_tbl} AS witbl ON "
        "ST_Within(intbl.{in_geom}, witbl.{wi_geom})"
    ).format(
        selcols=colSelect, in_tbl=inTbl, within_tbl=withinTbl,
        in_geom=inGeom, wi_geom=withinGeom
    )
    
    if apiToUse == "OGR_SPATIALITE":
        if outTblIsFile:
            from glass.geo.gt.attr import sel_by_attr
            
            sel_by_attr(db, Q, outTbl, api_gis='ogr')
        
        else:
            from glass.dct.to.sql import q_to_ntbl
            
            q_to_ntbl(db, outTbl, Q, api='ogr2ogr')
    
    elif apiToUse == 'POSTGIS':
        if outTblIsFile:
            if not geom_col:
                raise ValueError((
                    "To export a PostGIS table to file, geom_col "
                    "must be specified!"
                ))

            from glass.geo.gt.toshp.db import dbtbl_to_shp

            dbtbl_to_shp(
                db, Q, geom_col, outTbl, api="pgsql2shp",
                tableIsQuery=True)
        
        else:
            from glass.dct.to.sql import q_to_ntbl
            
            q_to_ntbl(db, outTbl, Q, api='psql')
    
    else:
        raise ValueError((
            "API {} is not available. OGR_SPATIALITE and POSTGIS "
            "are the only valid options"
        ))
    
    return outTbl


def feat_not_within(db, inTbl, inGeom, withinTbl, withinGeom, outTbl,
                    inTblCols=None, outTblIsFile=None,
                    apiToUse='OGR_SPATIALITE', geom_col=None):
    """
    Get features not Within with any of the features in withinTbl
    
    apiToUse options:
    * OGR_SPATIALITE;
    * POSTGIS.
    """
    
    from glass.pyt import obj_to_lst
    
    Q = (
        "SELECT {selCols} FROM {tbl} AS in_tbl WHERE ("
        "in_tbl.{in_geom} NOT IN ("
            "SELECT inin_tbl.{in_geom} FROM {wi_tbl} AS wi_tbl "
            "INNER JOIN {tbl} AS inin_tbl ON "
            "ST_Within(wi_tbl.{wi_geom}, inin_tbl.{in_geom})"
        "))"
    ).format(
        selCols = "*" if not inTblCols else ", ".join(obj_to_lst(inTblCols)),
        tbl     = inTbl, in_geom = inGeom, wi_tbl  = withinTbl,
        wi_geom = withinGeom
    )
    
    if apiToUse == "OGR_SPATIALITE":
        if outTblIsFile:
            from glass.geo.gt.attr import sel_by_attr
            
            sel_by_attr(db, Q, outTbl, api_gis='ogr')
        
        else:
            from glass.dct.to.sql import q_to_ntbl
            
            q_to_ntbl(db, outTbl, Q, api='ogr2ogr')
    
    elif apiToUse == "POSTGIS":
        if outTblIsFile:
            if not geom_col:
                raise ValueError((
                    "To export a PostGIS table to file, "
                    "geom_col must be specified"
                ))

            from glass.geo.gt.toshp.db import dbtbl_to_shp
            
            dbtbl_to_shp(
                db, Q, geom_col, outTbl, api='pgsql2shp',
                tableIsQuery=True
            )
        
        else:
            from glass.dct.to.sql import q_to_ntbl
            
            q_to_ntbl(db, outTbl, Q, api='psql')
    
    else:
        raise ValueError((
            "API {} is not available. OGR_SPATIALITE and POSTGIS "
            "are the only valid options"
        ))
    
    return outTbl


def intersect_in_same_table(db_name, table, geomA, geomB, outtable,
                            intersectField='intersects',
                            intersectGeom=None, colsSel=None):
    """
    Intersect two Geometries in the same table
    """
    
    from glass.pyt    import obj_to_lst
    from glass.dct.to.sql import q_to_ntbl
    
    COLS = obj_to_lst(colsSel)
    
    return q_to_ntbl(db_name, outtable, (
        "SELECT {cls}, CASE WHEN interse IS TRUE THEN 1 ELSE 0 END AS {intF} "
         "{intgeomF}FROM ("
            "SELECT {cls}, ST_Intersects({gA}, {gB}) AS interse "
            "{intgeom}FROM {t}"
         ") AS tst"
    ).format(
        gA=geomA, gB=geomB, t=table, intF=intersectField,
        cls="*" if not COLS else ", ".join(COLS),
        intgeom= "" if not intersectGeom else \
            ", ST_Intersection({}, {}) AS intersect_geom".format(
                geomA, geomB
            ),
        intgeomF = "" if not intersectGeom else ", intersect_geom"
    ), api='psql')


def line_intersection_pnt(db, inTbl, outTbl):
    """
    Get Points where two line features of the same feature class
    intersects.
    """
    
    from glass.dct.to.sql import q_to_ntbl
    
    # Get Points representing intersection
    Q_a = (
        "SELECT foo.gid, "
        "ST_Intersection(foo.geom, foo2.tstgeom) AS geom "
        "FROM (SELECT gid, geom FROM {t}) AS foo, ("
            "SELECT gid AS tstfid, geom AS tstgeom "
            "FROM {t}"
        ") AS foo2 "
        "WHERE foo.gid <> foo2.tstfid AND "
        "ST_Intersects(foo.geom, foo2.tstgeom)"
    ).format(t=inTbl)
    
    Q_b = (
        "SELECT gid AS ogid, (ST_Dump(geom)).geom AS geom FROM ("
            "SELECT gid, "
            "CASE "
                "WHEN ST_GeometryType(geom) = 'ST_LineString' "
                "THEN ST_Collect(ST_StartPoint(geom), ST_EndPoint(geom)) "
                "ELSE geom "
            "END AS geom FROM ("
                "SELECT gid, (ST_Dump(geom)).geom AS geom "
                "FROM ({t}) AS ttbl"
            ") AS tbl"
        ") AS tbll"
    ).format(t=Q_a)
    
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
            "FROM {bpnt} AS mtbl INNER JOIN ("
                "SELECT gid, ST_StartPoint(geom) AS st_pnt, "
                "ST_EndPoint(geom) AS end_pnt FROM ("
                    "SELECT gid, (ST_Dump(geom)).geom AS geom "
                    "FROM {t}"
                ") AS foo"
            ") AS st_tbl "
            "ON mtbl.ogid = st_tbl.gid"
        ") AS foo WHERE is_start = 0 AND is_end = 0"
    ).format(bpnt=allpnt, t=inTbl)
    
    return q_to_ntbl(db, outTbl, Q_main)


def del_topoerror_shps(db, shps, epsg, outfolder):
    """
    Remove topological errors from Feature Class data using PostGIS
    """
    
    import os
    from glass.pyt         import obj_to_lst
    from glass.sql.i       import cols_name
    from glass.dct.to.sql      import q_to_ntbl
    from glass.geo.gql.to      import shp_to_psql
    from glass.geo.gt.toshp.db import dbtbl_to_shp
    
    shps = obj_to_lst(shps)
    
    TABLES = shp_to_psql(db, shps, srsEpsgCode=epsg, api="shp2pgsql")
    
    NTABLE = [q_to_ntbl(
        db, "nt_{}".format(t),
        "SELECT {cols}, ST_MakeValid({tbl}.geom) AS geom FROM {tbl}".format(
            cols = ", ".join(["{}.{}".format(TABLES[t], x) for x in cols_name(
                db, TABLES[t], sanitizeSpecialWords=None
            ) if x != 'geom']),
            tbl=TABLES[t]
        ), api='psql'
    ) for t in range(len(TABLES))]
    
    for t in range(len(NTABLE)):
        dbtbl_to_shp(db, NTABLE[t], "geom", os.path.join(
            outfolder, TABLES[t]), tableIsQuery=None, api='pgsql2shp')


def intersection(dbname, aShp, bShp, pk, aGeom, bGeom, output,
                 primitive, priority, new_pk='fid_pk', new_geom='geom'):
    """
    Intersect two layers

    primitive is the geometric primitive (point, line, polygons)

    priority is an indication of the fields that the user wants to include in
    the output - fields of aShp or fields of bShp.
    The user could giver a list (with fields for selection) as value for the
    priority argument.
    """
    
    from glass.sql.c import sqlcon
    from glass.sql.i import cols_name

    if priority == 'a':
        cols_tbl = cols_name(dbname, aShp)
        cols_tbl.remove(aGeom)
    elif priority == 'b':
        cols_tbl = cols_name(dbname, bShp)
        cols_tbl.remove(bGeom)
    elif type(priority) == type([0]):
        cols_tbl = priority
    cols_tbl.remove(pk)
    conn = sqlcon(dbname, sqlAPI='psql')
    cursor = conn.cursor()

    if primitive == 'point':
        cols_tbl = ['{t}.{c}'.format(t=aShp, c=x) for x in cols_tbl]
        if priority == 'a':
            sel_geom = "{f}.{g}".format(f=aShp, g=aGeom)
        elif priority == 'b' or type(priority) == type([]):
            sel_geom = "{f}.{g}".format(f=bShp, g=bGeom)
        cursor.execute((
            "CREATE TABLE {out} AS SELECT {cols}, {int_geom} AS {ngeom} FROM {pnt} "
            "INNER JOIN {poly} ON ST_Within({pnt}.{geom_a}, "
            "{poly}.{geom_b});").format(
                out=output,
                cols=','.join(cols_tbl),
                pnt=aShp,
                geom_a=aGeom,
                geom_b=bGeom,
                poly=bShp,
                int_geom=sel_geom, ngeom=new_geom
        ))

    elif primitive == 'line':
        cols_tbl = ['{t}.{c}'.format(t=output, c=x) for x in cols_tbl]
        cols_tbl.append(new_geom)
        cursor.execute((
            "CREATE TABLE {out} AS SELECT {cols} FROM (SELECT {shp_a}.*, "
            "(ST_DUMP(ST_Intersection({shp_b}.geom, {shp_a}.{geom_fld}))).geom "
            "FROM {shp_b} INNER JOIN {shp_a} ON ST_Intersects({shp_b}.geom, "
            "{shp_a}.{geom_fld})) As {out} WHERE ST_Dimension({out}.geom) = "
            "1;").format(
                out=output,
                cols=','.join(cols_tbl),
                shp_a=aShp,
                shp_b=bShp,
                geom_fld=aGeom
        ))

    elif primitive == 'polygon':
        cols_tbl = ['{t}.{c}'.format(t=aShp, c=x) for x in cols_tbl]
        cursor.execute((
            'CREATE TABLE {out} AS SELECT {cols}, ST_Multi(ST_Buffer'
            '(ST_Intersection({shp_b}.geom, {shp_a}.{geom_fld}), 0.0)) As '
            '{ngeom} FROM {shp_b} INNER JOIN {shp_a} ON ST_Intersects({shp_b}.geom, '
            '{shp_a}.{geom_fld}) WHERE Not ST_IsEmpty(ST_Buffer('
            'ST_Intersection({shp_b}.geom, {shp_a}.{geom_fld}), 0.0));').format(
                out=output,
                cols=','.join(cols_tbl),
                shp_a=aShp,
                shp_b = bShp,
                geom_fld=aGeom, ngeom=new_geom
        ))

    cursor.execute(
        "ALTER TABLE {out} ADD COLUMN {fid_pk} BIGSERIAL PRIMARY KEY;".format(
            out=output, fid_pk=new_pk))

    conn.commit()
    cursor.close()
    conn.close()
    return output, new_pk, new_geom


def check_autofc_overlap(checkShp, epsg, dbname, outOverlaps):
    """
    Check if the features of one Feature Class overlaps each other
    """
    
    import os
    from glass.sql.db      import create_db
    from glass.dct.to.sql      import q_to_ntbl
    from glass.geo.gql.to      import shp_to_psql
    from glass.geo.gt.toshp.db import dbtbl_to_shp
    
    create_db(dbname, api='psql')
    
    # Send data to postgresql
    table = shp_to_psql(dbname, checkShp, srsEpsgCode=epsg, api="pandas")
    
    # Produce result
    q = (
        "SELECT foo.* FROM ("
            "SELECT * FROM {t}"
        ") AS foo, ("
            "SELECT cat AS relcat, geom AS tst_geom FROM {t}"
        ") AS foo2 "
        "WHERE ("
            "ST_Overlaps(geom, tst_geom) IS TRUE OR "
            "ST_Equals(geom, tst_geom) IS TRUE OR "
            "ST_Contains(geom, tst_geom) IS TRUE"
        ") AND cat <> relcat"
    ).format(t=table)
    
    resultTable = os.path.splitext(os.path.basename(outOverlaps))[0]
    q_to_ntbl(dbname, resultTable, q, api='psql')
    
    dbtbl_to_shp(
        dbname, resultTable, "geom", outOverlaps, api='psql', epsg=epsg)
    
    return outOverlaps


def pg_erase(db, inTbl, eraseTbl, inGeom, eraseGeom, outTbl):
    """
    Erase
    """
    
    from glass.sql.i  import cols_name
    from glass.dct.to.sql import q_to_ntbl
    
    cols = ["mtbl.{}".format(
        x) for x in cols_name(db, inTbl, api='psql') if x != inGeom]
    
    q = (
        "SELECT {}, ST_Difference(mtbl.{}, foo.erase_geom) AS {} "
        "FROM {} AS mtbl, "
        "("
            "SELECT ST_UnaryUnion(ST_Collect(eetbl.{})) AS erase_geom "
            "FROM {} AS eetbl "
            "INNER JOIN {} AS jtbl ON ST_Intersects(eetbl.{}, jtbl.{})"
        ") AS foo"
    ).format(
        ", ".join(cols), inGeom, inGeom, inTbl, eraseGeom, eraseTbl,
        inTbl, eraseGeom, inGeom
    )
    
    return q_to_ntbl(db, outTbl, q, api='psql')


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
    
    import os
    
    if not pntSelect and not polySelect:
        raise ValueError("You have to select something")
    
    sql = (
        "SELECT {colPnt}{colPoly} FROM {pnt_tq} "
        "INNER JOIN {poly_tq} ON "
        "ST_Within({pnt}.{pnGeom}, {poly}.{pgeom})"
    ).format(
        colPnt  = pntSelect if pntSelect else "",
        colPoly = polySelect if polySelect and not pntSelect else \
            ", " + polySelect if polySelect and pntSelect else "",
        pnt_tq  = pntTbl if not pntQuery else pntQuery,
        poly_tq = polyTbl if not polyQuery else polyQuery,
        pnt     = pntTbl,
        poly    = polyTbl,
        pnGeom  = pntGeom,
        pgeom   = polyGeom
    )
    
    if outTblIsFile:
        from glass.geo.gt.attr import sel_by_attr
        
        sel_by_attr(sqDB, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.dct.to.sql import q_to_ntbl
        
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
    
    import os
    
    if not polySelect:
        raise ValueError("Man, select something!")
    
    sql = (
        "SELECT {selCols} FROM {polTable} WHERE ("
        "{polName}.{polGeom} not in ("
            "SELECT {polName}.{polGeom} FROM {pntTable} "
            "INNER JOIN {polTable} ON "
            "ST_Within({pntName}.{pntGeom_}, {polName}.{polGeom})"
        "))"
    ).format(
        selCols  = "*" if not polySelect else polySelect,
        polTable = polyTbl if not polyQuery else polyQuery,
        polGeom  = polyGeom,
        pntTable = pntTbl if not pntQuery else pntQuery,
        pntGeom_ = pntGeom,
        pntName  = pntTbl,
        polName  = polyTbl
    )
    
    if outTblIsFile:
        from glass.geo.gt.attr import sel_by_attr
        
        sel_by_attr(sqBD, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.dct.to.sql import q_to_ntbl
        
        q_to_ntbl(sqBD, outTbl, sql, api='ogr2ogr')

