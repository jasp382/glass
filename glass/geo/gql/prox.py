"""
Tools for process geographic data on PostGIS
"""


def st_near(db, inTbl, inGeom, nearTbl, nearGeom, output,
            near_col='near', api='psql', whrNear=None, outIsFile=None,
            until_dist=None, cols_in_tbl=None, intbl_pk=None,
            cols_near_tbl=None):
    """
    Near tool for PostGIS and Spatialite

    api options:
    * psql
    * splite or spatialite
    """
    
    if api == 'psql' and not intbl_pk:
        from glass.pyt    import obj_to_lst
        from glass.dct.to.sql import q_to_ntbl
    
        _out = q_to_ntbl(db, output, (
            "SELECT m.*, ST_Distance(m.{ingeom}, j.geom) AS {distCol} "
            "FROM {t} AS m, ("
                "SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
                "FROM {tblNear}{nearwhr}"
            ") AS j"
        ).format(
            ingeom=inGeom, distCol=near_col, t=inTbl, neargeom=nearGeom,
            tblNear=nearTbl
        ), api='psql')

        return output
    
    elif api == 'psql' and intbl_pk:
        from glass.pyt    import obj_to_lst
        from glass.dct.to.sql import q_to_ntbl

        _out = q_to_ntbl(db, output, (
            "SELECT DISTINCT ON (s.{col_pk}) "
            "{inTblCols}, {nearTblCols}"
            "ST_Distance("
                "s.{ingeomCol}, h.{negeomCol}"
            ") AS {nearCol} FROM {in_tbl} AS s "
            "LEFT JOIN {near_tbl} AS h "
            "ON ST_DWithin(s.{ingeomCol}, h.{negeomCol}, {dist_v}) "
            "ORDER BY s.{col_pk}, ST_Distance(s.{ingeomCol}, h.{negeomCol})"
        ).format(
            col_pk=intbl_pk, 
            inTblCols="s.*" if not cols_in_tbl else ", ".join([
                "s.{}".format(x) for x in obj_to_lst(cols_in_tbl)
            ]),
            nearTblCols="" if not cols_near_tbl else ", ".join([
                "h.{}".format(x) for x in obj_to_lst(cols_near_tbl)
            ]) + ", ",
            ingeomCol=inGeom, negeomCol=nearGeom,
            nearCol=near_col, in_tbl=inTbl, near_tbl=nearTbl,
            dist_v="100000" if not until_dist else until_dist
        ), api='psql')

        return output
    
    elif api == 'splite' or api == 'spatialite':
        Q = (
            "SELECT m.*, ST_Distance(m.{ingeom}, j.geom) AS {distCol} "
            "FROM {t} AS m, ("
                "SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
                "FROM {tblNear}{nearwhr}"
            ") AS j"
        ).format(
            ingeom=inGeom, distCol=near_col, t=inTbl,
            neargeom=nearGeom, tblNear=nearTbl,
            nearwhr="" if not whrNear else " WHERE {}".format(whrNear)
        )

        if outIsFile:
            from glass.geo.gt.attr import sel_by_attr

            sel_by_attr(db, Q, output, api_gis='ogr')
        
        else:
            from glass.dct.to.sql import q_to_ntbl

            q_to_ntbl(db, output, Q, api='ogr2ogr')
    
        return output
    
    else:
        raise ValueError("api {} does not exist!".format(api))


def st_buffer(db, inTbl, bfDist, geomCol, outTbl, bufferField="geometry",
              whrClause=None, dissolve=None, cols_select=None, outTblIsFile=None):
    """
    Using Buffer on PostGIS Data
    """
    
    from glass.pyt import obj_to_lst
    
    dissolve = obj_to_lst(dissolve) if dissolve != "ALL" else "ALL"
    
    SEL_COLS = "" if not cols_select else ", ".join(obj_to_lst(cols_select))
    DISS_COLS = "" if not dissolve or dissolve == "ALL" else ", ".join(dissolve)
    GRP_BY = "" if not dissolve else "{}, {}".format(SEL_COLS, DISS_COLS) if \
        SEL_COLS != "" and DISS_COLS != "" else SEL_COLS \
        if SEL_COLS != "" else DISS_COLS if DISS_COLS != "" else ""
    
    Q = (
        "SELECT{sel}{spFunc}{geom}, {_dist}{endFunc} AS {bf} "
        "FROM {t}{whr}{grpBy}"
    ).format(
        sel = " " if not cols_select else " {}, ".format(SEL_COLS),
        spFunc="ST_Buffer(" if not dissolve else \
            "ST_UnaryUnion(ST_Collect(ST_Buffer(",
        geom=geomCol, _dist=bfDist,
        endFunc=")" if not dissolve else ")))",
        t=inTbl,
        grpBy=" GROUP BY {}".format(GRP_BY) if GRP_BY != "" else "",
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        bf=bufferField
    )
    
    if not outTblIsFile:
        from glass.dct.to.sql import q_to_ntbl
        
        outTbl = q_to_ntbl(db, outTbl, Q, api='psql')
    
    else:
        from glass.geo.gt.toshp.db import dbtbl_to_shp
        
        dbtbl_to_shp(db, Q, bufferField, outTbl, api='pgsql2shp',
            tableIsQuery=True
        )
    
    return outTbl

def splite_buffer(db, table, dist, geomField, outTbl,
              cols_select=None, bufferField="geometry",
              whrClause=None, outTblIsFile=None, dissolve=None):
    """
    Run ST_Buffer
    
    if not dissolve, no generalization will be applied; 
    if dissolve == to str or list, a generalization will be accomplish
    using the fields referenced by this object;
    if dissolve == 'ALL', all features will be dissolved.
    """
    
    from glass.pyt import obj_to_lst
    
    dissolve = obj_to_lst(dissolve) if dissolve != "ALL" else "ALL"
    
    sql = (
        "SELECT{sel}{spFunc}{geom}, {_dist}{endFunc} AS {bf} "
        "FROM {tbl}{whr}{grpBy}"
    ).format(
        sel = " " if not cols_select else " {}, ".format(
            ", ".join(obj_to_lst(cols_select))
        ),
        tbl=table,
        geom=geomField, _dist=str(dist), bf=bufferField,
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        spFunc="ST_Buffer(" if not dissolve else \
            "ST_UnaryUnion(ST_Collect(ST_Buffer(",
        endFunc = ")" if not dissolve else ")))",
        grpBy="" if not dissolve or dissolve == "ALL" else " GROUP BY {}".format(
            ", ".join(dissolve)
        )
    )
    
    if outTblIsFile:
        from glass.geo.gt.attr import sel_by_attr
        
        sel_by_attr(db, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.dct.to.sql import q_to_ntbl
        
        q_to_ntbl(db, outTbl, sql, api='ogr2ogr')
    
    return outTbl

