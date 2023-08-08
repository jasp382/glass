"""
Do Something with features
"""


def multipart_to_shp(shp, oshp):
    """
    ID multipart features in a Feature Class
    and export them to a new feature class
    """

    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    df = shp_to_obj(shp)

    df["geomtype"] = df.geometry.geom_type

    df = df[df.geomtype == 'MultiLineString']

    df_to_shp(df, oshp)

    return oshp



def id_isolated_lines(shp, oshp):
    """
    ID Isolated lines

    Lines not touching with others
    """

    from glass.pys.oss  import fprop
    from glass.sql.db   import create_db
    from glass.prop.prj import shp_epsg
    from glass.it.db    import shp_to_psql
    from glass.it.shp   import dbtbl_to_shp

    epsg = shp_epsg(shp)

    # Create DB
    db = create_db(
        fprop(shp, 'fn', forceLower=True),
        api='psql', overwrite=True
    )

    # Send data to db
    intbl = shp_to_psql(
        db, shp, api="shp2pgsql",
        srsEpsgCode=epsg, encoding="LATIN1"
    )

    # Run Query
    id_endpnt = (
        "SELECT gid, geom, "
        "ST_AsText(ST_StartPoint(geom)) AS pstart, "
        "ST_AsText(ST_EndPoint(geom)) AS pend "
        "FROM ("
            "SELECT gid, (ST_Dump(geom)).geom AS geom "
            f"FROM {intbl}"
        ") AS foo"
    )

    count_endpnt = (
        "ROW_NUMBER() OVER (ORDER BY txtgeom) AS idpnt, "
        "txtgeom, npnt FROM ("
            "SELECT txtgeom, COUNT(txtgeom) AS npnt "
            "FROM ("
                "SELECT pstart AS txtgeom "
                f"FROM ({id_endpnt}) AS ta "
                "UNION ALL "
                "SELECT pend AS txtgeom "
                f"FROM ({id_endpnt}) AS tb"
            ") AS tbl "
            "GROUP BY txtgeom"
        ") AS cntpnt "
        "WHERE npnt = 1"
    )

    q = (
        "SELECT mtbl.*, st_tbl.npnt AS nstart, en_tbl.npnt AS nend "
        f"FROM ({id_endpnt}) AS mtbl "
        f"LEFT JOIN ({count_endpnt}) AS st_tbl "
        "ON mtbl.pstart = st_tbl.txtgeom "
        f"LEFT JOIN ({count_endpnt}) AS en_tbl "
        "ON mtbl.pend = en_tbl.txtgeom "
        "WHERE st_tbl.npnt = 1 AND en_tbl.npnt = 1 "
        "ORDER BY mtbl.gid"
    )

    dbtbl_to_shp(
        db, q, "geom", oshp, inDB='psql',
        tableIsQuery=True
    )

    return oshp


def id_some_lines(shp, oshp):
    """
    """

    from glass.pys.oss  import fprop
    from glass.sql.db   import create_db
    from glass.prop.prj import shp_epsg
    from glass.it.db    import shp_to_psql
    from glass.it.shp   import dbtbl_to_shp

    epsg = shp_epsg(shp)

    # Create DB
    db = create_db(
        fprop(shp, 'fn', forceLower=True),
        api='psql', overwrite=True
    )

    # Send data to db
    intbl = shp_to_psql(
        db, shp, api="shp2pgsql",
        srsEpsgCode=epsg, encoding="LATIN1"
    )

    # Run Query
    id_endpnt = (
        "SELECT gid, geom, "
        "ST_AsText(ST_StartPoint(geom)) AS pstart, "
        "ST_AsText(ST_EndPoint(geom)) AS pend "
        "FROM ("
            "SELECT gid, (ST_Dump(geom)).geom AS geom "
            f"FROM {intbl}"
        ") AS foo"
    )

    count_endpnt = (
        "ROW_NUMBER() OVER (ORDER BY txtgeom) AS idpnt, "
        "txtgeom, npnt FROM ("
            "SELECT txtgeom, COUNT(txtgeom) AS npnt "
            "FROM ("
                "SELECT pstart AS txtgeom "
                f"FROM ({id_endpnt}) AS ta "
                "UNION ALL "
                "SELECT pend AS txtgeom "
                f"FROM ({id_endpnt}) AS tb"
            ") AS tbl "
            "GROUP BY txtgeom"
        ") AS cntpnt "
    )

    count_endpnt_ = f"{count_endpnt} WHERE npnt = 1"

    q_ = (
        "SELECT mtbl.gid, mtbl.pstart, mtbl.pend, mtbl.geom "
        "ST_StartPoint(mtbl.geom) AS lstart, "
        "ST_EndPoint(mtbl.geom) AS lend, "
        "st_tbl.npnt AS nstart, en_tbl.npnt AS nend "
        f"FROM ({id_endpnt}) AS mtbl "
        f"LEFT JOIN ({count_endpnt_}) AS st_tbl "
        "ON mtbl.pstart = st_tbl.txtgeom "
        f"LEFT JOIN ({count_endpnt_}) AS en_tbl "
        "ON mtbl.pend = en_tbl.txtgeom "
        "ORDER BY mtbl.gid"
    )

    q = (
        "SELECT * FROM ("
            "SELECT gid, geom, "
            "CASE "
                "WHEN startdist = 0 THEN enddist ELSE startdist "
            "END AS neardist FROM ("
                "SELECT mt.gid, mt.geom, "
                "MIN(ST_Distance(mt.lstart, nt.geom)) AS startdist, "
                "MIN(ST_Distance(mt.lend, nt.geom)) AS enddist "
                f"FROM ({q_}) AS mt, ("
                    "SELECT ROW_NUMBER() OVER (ORDER BY txtgeom) AS idpnt, "
                    "txtgeom, npnt, "
                    f"ST_GeomFromText(txtgeom, {str(epsg)}) AS geom "
                    "FROM ("
                        "SELECT txtgeom, COUNT(txtgeom) AS npnt FROM ("
                            "SELECT pstart AS txtgeom "
                            f"FROM ({id_endpnt}) AS ta "
                            "UNION ALL "
                            "SELECT pend AS txtgeom "
                            f"FROM ({id_endpnt} AS tb "
                        ") AS tbl "
                        "GROUP BY txtgeom"
                    ") AS cntpnt"
                ") AS nt "
                "WHERE (mt.nstart = 1 AND mt.nend IS NULL "
                "AND mt.pstart <> nt.txtgeom) OR "
                "(mt.nstart IS NULL AND mt.nend = 1 AND mt.pend <> nt.txtgeom) "
                "GROUP BY gid"
            ") AS foo"
        ") AS coco "
        "WHERE neardist < 50"
    )

    dbtbl_to_shp(
        db, q, "geom", oshp, inDB='psql',
        tableIsQuery=True
    )

    return oshp

