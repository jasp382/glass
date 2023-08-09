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

        poly = prj_ogrgeom(
            polygon, epsg, outEpsg,
            api="ogr" if epsg != 4326 else 'shapely'
        )

        return poly
    else:
        return polygon


def ext_to_polygon(ingeo, out_srs=None, outaswkt=None):
    """
    Read one feature class/raster extent 
    and create a boundary with that
    extent
    """

    from glass.prop.ext import get_ext
    from glass.gobj     import create_polygon

    # Get Extent
    ext = get_ext(ingeo)

    # Create points of the new boundary based on the extent
    boundary_points = [
        (ext[0], ext[3]), (ext[1], ext[3]),
        (ext[1], ext[2]), (ext[0], ext[2]), (ext[0], ext[3])
    ]

    polygon = create_polygon(boundary_points)

    if out_srs:
        from glass.prop.prj import get_epsg

        in_srs = get_epsg(ingeo)

        if in_srs != out_srs:
            from glass.prj.obj import prj_ogrgeom

            polygon = prj_ogrgeom(polygon, in_srs, out_srs,
                api='shply')
    
    polygon.FlattenTo2D()
    
    return polygon if not outaswkt else polygon.ExportToWkt()

