"""
Geometric Conversion
"""

from glass.prop.prj import get_epsg
from glass.prj.obj  import prj_ogrgeom
from glass.gobj     import create_polygon


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


def ext_to_polygon(ingeo, out_srs=None, outaswkt=None, geolyr=None):
    """
    Read one feature class/raster extent 
    and create a boundary with that
    extent
    """

    from glass.prop.ext import get_ext

    # Get Extent
    ext = get_ext(ingeo, geolyr=geolyr)

    # Create points of the new boundary based on the extent
    boundary_points = [
        (ext[0], ext[3]), (ext[1], ext[3]),
        (ext[1], ext[2]), (ext[0], ext[2]), (ext[0], ext[3])
    ]

    polygon = create_polygon(boundary_points)

    if out_srs:
        in_srs = get_epsg(ingeo, lyrname=geolyr)

        if in_srs != out_srs:
            polygon = prj_ogrgeom(polygon, in_srs, out_srs,
                api='shply')
    
    polygon.FlattenTo2D()
    
    return polygon if not outaswkt else polygon.ExportToWkt()


def featext_to_polygon(ingeo, feat_id=None, out_srs=None, outaswkt=None, geolyr=None):
    """
    Features extent to polygons
    """

    from osgeo import ogr
    from glass.prop.df import drv_name

    isrs = None if not out_srs else get_epsg(ingeo)

    drv = drv_name(ingeo) if '.gdb' not in ingeo \
        else 'OpenFileGDB'

    src = ogr.GetDriverByName(drv).Open(ingeo)
    lyr = src.GetLayer() if not geolyr else src.GetLayer(geolyr)

    bnds, refattr = [], []

    for feat in lyr:
        geom = feat.GetGeometryRef()
        ext  = geom.GetEnvelope()

        pnts = [
            (ext[0], ext[3]), (ext[1], ext[3]),
            (ext[1], ext[2]), (ext[0], ext[2]), (ext[0], ext[3])
        ]

        polygon = create_polygon(pnts)

        if out_srs:
            if isrs != out_srs:
                polygon = prj_ogrgeom(polygon, isrs, out_srs, api='shply')
        
        polygon.FlattenTo2D()
        
        bnds.append(polygon if not outaswkt else polygon.ExportToWkt())

        refattr.append(feat.GetField(feat_id) \
            if type(feat_id) == str else feat.GetFID())
        
    return bnds, refattr

