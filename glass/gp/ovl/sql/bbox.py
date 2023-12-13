"""
Overlay Operations using PostGIS
"""

def geoms_equal_to_bound(db, tbl, geomcol, tblsrs, topleft, bottomright, epsg):
    """
    Returns geometries equal to a boundary

    Logic:
        - create points with rst extent 
        - compare whether distance between created points and cell geom is equal to 0 (0.000001)
    """

    from glass.sql.q import q_to_obj

    left, top = topleft
    right, bottom = bottomright

    q = (
        "SELECT * FROM ("
            "SELECT tgrid.gid, tgrid.cellid, "
            "ST_Distance(ST_SetSRID(ST_MakePoint("
                f"ST_XMin({geomcol}), ST_YMax({geomcol})), {int(tblsrs)}), "
                f"ST_GeomFromText('POINT ({str(left)} {str(top)} 0)', {int(epsg)})"
            ") AS dist_topleft, "
            "ST_Distance(ST_SetSRID(ST_MakePoint("
                f"ST_XMax({geomcol}), ST_YMax({geomcol})), {int(tblsrs)}), "
                f"ST_GeomFromText('POINT ({str(right)} {str(top)} 0)', {int(epsg)})"
            ") AS dist_topright, "
            "ST_Distance(ST_SetSRID(ST_MakePoint("
                f"ST_XMax({geomcol}), ST_YMin({geomcol})), {int(tblsrs)}), "
                f"ST_GeomFromText('POINT ({str(right)} {str(bottom)} 0)', {int(epsg)})"
            ") AS dist_lowright, "
            "ST_Distance(ST_SetSRID(ST_MakePoint("
                f"ST_XMin({geomcol}), ST_YMin({geomcol})), {int(tblsrs)}), "
                f"ST_GeomFromText('POINT ({str(left)} {str(bottom)} 0)', {int(epsg)})"
            ") AS dist_lowleft "
            f"FROM {tbl} AS tgrid"
        ") AS foo "
        "WHERE dist_topleft < 0.000001 AND dist_topright < 0.000001 "
        "AND dist_lowright < 0.000001 AND dist_lowleft < 0.000001"
    )

    df = q_to_obj(db, q)

    return df

