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

