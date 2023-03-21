"""
Tools for process geographic data on PostGIS
"""


def st_near(db, inTbl, inGeom, nearTbl, nearGeom, output=None,
            near_col='near', api='psql', whrNear=None, outIsFile=None,
            until_dist=None, cols_in_tbl=None, intbl_pk=None,
            cols_near_tbl=None):
    """
    Near tool for PostGIS and Spatialite

    api options:
    * psql
    * splite or spatialite
    """

    from glass.pys   import obj_to_lst
    from glass.sql.q import q_to_ntbl
    
    if api == 'psql' and not intbl_pk:
        icols = "s.*" if not cols_in_tbl else ", ".join([
            f"s.{x}" for x in obj_to_lst(cols_in_tbl)
        ])
        ncols = "" if not cols_near_tbl else ", ".join([
            f"h.{x}" for x in obj_to_lst(cols_near_tbl)
        ]) + ", "

        dist_v = "100000" if not until_dist else until_dist

        q = (
            f"SELECT {icols}, {ncols}"
            f"ST_Distance(s.{inGeom}, h.geom) AS {near_col} "
            f"FROM {inTbl} AS s, ("
                f"SELECT ST_UnaryUnion(ST_Collect({nearGeom})) AS geom "
                f"FROM {nearTbl}{whrNear}"
            ") AS h"
        ) if not intbl_pk else (
            f"SELECT DISTINCT ON (s.{intbl_pk}) "
            f"{icols}, {ncols}"
            f"ST_Distance(s.{inGeom}, h.{nearGeom}) AS {near_col} "
            f"FROM {inTbl} AS s "
            f"LEFT JOIN {nearTbl} AS h "
            f"ON ST_DWithin(s.{inGeom}, h.{nearGeom}, {dist_v}) "
            f"ORDER BY s.{intbl_pk}, ST_Distance(s.{inGeom}, h.{nearGeom})"
        )

        if output:
            return q_to_ntbl(db, output, q, api='psql')

        return q
    
    elif api == 'splite' or api == 'spatialite':
        whr = "" if not whrNear else f" WHERE {whrNear}"
        Q = (
            f"SELECT m.*, ST_Distance(m.{inGeom}, j.geom) AS {near_col} "
            f"FROM {inTbl} AS m, ("
                f"SELECT ST_UnaryUnion(ST_Collect({nearGeom})) AS geom "
                f"FROM {nearTbl}{whr}"
            ") AS j"
        )

        if output and outIsFile:
            from glass.tbl.filter import sel_by_attr

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
