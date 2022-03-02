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
        from glass.pys   import obj_to_lst
        from glass.sql.q import q_to_ntbl
    
        _out = q_to_ntbl(db, output, (
            "SELECT m.*, ST_Distance(m.{ingeom}, j.geom) AS {distCol} "
            "FROM {t} AS m, ("
                "SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
                "FROM {tblNear}{nearwhr}"
            ") AS j"
        ).format(
            ingeom=inGeom, distCol=near_col, t=inTbl, neargeom=nearGeom,
            tblNear=nearTbl, nearwhr=whrNear
        ), api='psql')

        return output
    
    elif api == 'psql' and intbl_pk:
        from glass.pys   import obj_to_lst
        from glass.sql.q import q_to_ntbl

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
            from glass.tbl.filter import sel_by_attr

            sel_by_attr(db, Q, output, api_gis='ogr')
        
        else:
            from glass.sql.q import q_to_ntbl

            q_to_ntbl(db, output, Q, api='ogr2ogr')
    
        return output
    
    else:
        raise ValueError("api {} does not exist!".format(api))
