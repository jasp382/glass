"""
Geometric Conversion
"""


def coords_to_boundary(topLeft, lowerRight, epsg, outEpsg=None):
    """
    Top Left and Lower Right to Boundary
    """

    from glass.gobj import create_polygon

    boundary_points = [
        (   topLeft[0],    topLeft[1]),
        (lowerRight[0],    topLeft[1]),
        (lowerRight[0], lowerRight[1]),
        (   topLeft[0], lowerRight[1]),
        (   topLeft[0],    topLeft[1])
    ]

    # Create polygon
    polygon = create_polygon(boundary_points)

    # Convert SRS if outEPSG
    if outEpsg and epsg != outEpsg:
        from glass.prj.obj import prj_ogrgeom

        poly = prj_ogrgeom(polygon, epsg, outEpsg)

        return poly
    else:
        return polygon

