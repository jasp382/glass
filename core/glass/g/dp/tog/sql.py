"""
Something to Geometry
"""

def xycols_to_geom(db, intbl, x_col, y_col, outtable,
                   geom_field='geom', epsg=4326):
    """
    X and Y Colums to PostGIS Geom Column
    """
    
    from glass.ng.sql.q import q_to_ntbl
    
    return q_to_ntbl(db, outtable, (
        "SELECT *, ST_SetSRID(ST_MakePoint({}, {}), {}) AS {} "
        "FROM {}"
    ).format(
        x_col, y_col, str(epsg), geom_field, intbl
    ), api='psql')

