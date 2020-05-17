"""
Data to Geometry
"""



def shpext_to_boundary(in_shp, out_srs=None):
    """
    Read one feature class extent and create a boundary with that
    extent
    """

    from glass.prop.ext import get_ext
    from glass.gobj     import create_polygon

    # Get Extent
    ext = get_ext(in_shp)

    # Create points of the new boundary based on the extent
    boundary_points = [
        (ext[0], ext[3]), (ext[1], ext[3]),
        (ext[1], ext[2]), (ext[0], ext[2]), (ext[0], ext[3])
    ]
    polygon = create_polygon(boundary_points)

    if out_srs:
        from glass.prop.prj import shp_epsg

        in_srs = shp_epsg(in_shp)

        if in_srs != out_srs:
            from glass.prj.obj import prj_ogrgeom

            poly = prj_ogrgeom(polygon, in_srs, out_srs,
                api='shply')

            return poly
        
        else:
            return polygon
    else:
        return polygon

