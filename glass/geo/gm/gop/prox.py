"""
Bufering TOOLS
"""


def xy_to_buffer(x, y, radius):
    """
    XY Coordinates to Buffer Geometry
    """
    
    from glass.geo.gm.to import new_pnt
    
    pnt = new_pnt(x, y)
    
    return pnt.Buffer(int(round(float(radius), 0)))


def draw_buffer(geom, radius):
    return geom.Buffer(int(round(float(radius), 0)))


def df_buffer_extent(inDf, inEpsg, meterTolerance, geomCol="geometry",
    mantainOriginalGeom=None):
    """
    For all geometries, calculate the boundary given by 
    the sum between the feature extent and the Tolerance variable
    """

    from shapely.geometry import Polygon
    from geopandas  import GeoDataFrame as gdf
    from glass.geo.gm.ext import featext_to_dfcols

    inDf = featext_to_dfcols(inDf, geomCol)

    inDf['minx'] = inDf.minx - meterTolerance
    inDf['miny'] = inDf.miny - meterTolerance
    inDf['maxx'] = inDf.maxx + meterTolerance
    inDf['maxy'] = inDf.maxy + meterTolerance

    # Produce new geometries
    geoms = [Polygon([
        [ext[0], ext[3]], [ext[1], ext[3]],
        [ext[1], ext[2]], [ext[0], ext[2]],
        [ext[0], ext[3]]
    ]) for ext in zip(inDf.minx, inDf.maxx, inDf.miny, inDf.maxy)]

    # Delete uncessary columns
    dropCols = ['minx', 'miny', 'maxx', 'maxy']
    if mantainOriginalGeom:
        inDf.rename(columns={geomCol : 'old_geom'}, inplace=True)
    else:
        dropCols.append(geomCol)
    
    inDf.drop(dropCols, axis=1, inplace=True)

    resDf = gdf(inDf, crs={'init' : 'epsg:{}'.format(inEpsg)}, geometry=geoms)

    return resDf
