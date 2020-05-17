"""
Overlay operations with geometry objects
"""

def point_in_polygon(point, polygon):
    """
    Point is Inside Polygon?
    """
    
    return point.Within(polygon)


def count_pnt_inside_poly(pnt, cpnt, polys, pntattr=None):
    """
    Count points inside polygons
    """

    from shapely.wkt import loads

    cpnt = 'count_pnt' if not cpnt else cpnt

    def count_pnt_inside_mapunits(row):
        pg = loads(row.geometry.wkt)

        pnts = pnt.copy()

        pnts['tst_geom'] = pnts.geometry.intersects(pg)

        pnts = pnts[pnts.tst_geom == True]

        pnts.reset_index(drop=True, inplace=True)

        row[cpnt] = pnts.shape[0] if not pntattr else pnts[pntattr].sum()

        return row
    
    polys = polys.apply(lambda x: count_pnt_inside_mapunits(x), axis=1)

    return polys


def pnt_inside_poly(pnt, poly, pntgeom, polygeom, poly_cols_mantain=None,
    only_points_inside=True):
    """
    Two tables: one with points, other with polygons

    return a new table with the points related 
    with the polygon containing the point
    """

    from glass.pys import obj_to_lst

    poly_cols_mantain = obj_to_lst(poly_cols_mantain)
    poly_cols_mantain = [] if not poly_cols_mantain else poly_cols_mantain

    # Join the tables
    # each record of pnt table will be
    # related with each record of poly table
    # new table will have a number of records
    # equal to pnt records x poly records
    pnt['aid']  = 1
    poly['bid'] = 1

    pnt = pnt.merge(poly, how='left', left_on='aid', right_on='bid')

    # Check which polygons contain each point
    pnt['iscontain'] = pnt[polygeom].contains(pnt[pntgeom])

    dcols = [c for c in poly.columns.values \
        if c not in poly_cols_mantain] + ['aid']
    
    if only_points_inside:
        # Get final dataframe
        pnt = pnt[pnt.iscontain == True]

        pnt.reset_index(drop=True, inplace=True)

        dcols.append("iscontain")
    
    pnt.drop(dcols, axis=1, inplace=True)

    return pnt

