"""
Numerical to Shape
"""


"""
Extent to Shape
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


def shpext_to_boundshp(inShp, outShp, epsg=None):
    """
    Read one feature class extent and create a boundary with that
    extent
    
    The outFile could be a Feature Class or one Raster Dataset
    """
    
    from osgeo         import ogr
    from glass.prop.df import drv_name
    from glass.pys.oss import fprop
    
    # Get SRS for the output
    if not epsg:
        from glass.prop.prj import shp_ref
        
        srs = shp_ref(inShp)
    
    else:
        from glass.prop.prj import sref_from_epsg
        
        srs= sref_from_epsg(epsg)
    
    # Write new file
    shp = ogr.GetDriverByName(
        drv_name(outShp)).CreateDataSource(outShp)
    
    lyr = shp.CreateLayer(
        fprop(outShp, 'fn', forceLower=True),
        srs, geom_type=ogr.wkbPolygon
    )
    
    outDefn = lyr.GetLayerDefn()
    
    feat = ogr.Feature(outDefn)
    polygon = shpext_to_boundary(inShp)
    
    feat.SetGeometry(polygon)
    lyr.CreateFeature(feat)
    
    feat.Destroy()
    shp.Destroy()
    
    return outShp


def featext_to_shp(shp, oshp, epsg=None):
    """
    Get extent of each feature and save it on a new shapefile
    """

    from shapely.geometry import Polygon
    from geopandas import GeoDataFrame as gdf
    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp
    from glass.prop.prj import shp_epsg
    from glass.prop.ext import featext_to_dfcols

    idf = shp_to_obj(shp)

    epsg = shp_epsg(shp) if not epsg else epsg

    idf = featext_to_dfcols(idf, "geometry")

    # Get new geometries
    geoms = [Polygon([
        [ext[0], ext[3]], [ext[1], ext[3]],
        [ext[1], ext[2]], [ext[0], ext[2]],
        [ext[0], ext[3]]
    ]) for ext in zip(idf.minx, idf.maxx, idf.miny, idf.maxy)]

    # Delete columns
    dropCols = ['minx', 'miny', 'maxx', 'maxy', "geometry"]
    idf.drop(dropCols, axis=1, inplace=True)

    rdf = gdf(idf, crs=f"EPSG:{str(epsg)}", geometry=geoms)

    of = df_to_shp(rdf, oshp)

    return of

