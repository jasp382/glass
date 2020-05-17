"""
Bufering TOOLS
"""

def geoseries_buffer(gseries, dist):
    """
    Buffer of GeoSeries
    """
    
    return gseries.buffer(dist, resolution=16)


def xy_to_buffer(x, y, radius):
    """
    XY Coordinates to Buffer Geometry
    """
    
    from glass.g.gobj import new_pnt
    
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

    from shapely.geometry  import Polygon
    from geopandas         import GeoDataFrame as gdf
    from glass.g.gp.ext.pd import featext_to_dfcols

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

    resDf = gdf(inDf, crs='EPSG:{}'.format(inEpsg), geometry=geoms)

    return resDf


def geodf_buffer_to_shp(geoDf, dist, outfile, colgeom='geometry'):
    """
    Execute the Buffer Function of GeoPandas and export
    the result to a new shp
    """
    
    from glass.g.wt.shp import df_to_shp
    
    __geoDf = geoDf.copy()
    __geoDf["buffer_geom"] = __geoDf[colgeom].buffer(dist, resolution=16)
    
    __geoDf.drop(colgeom, axis=1, inplace=True)
    __geoDf.rename(columns={"buffer_geom" : colgeom}, inplace=True)
    
    df_to_shp(__geoDf, outfile)
    
    return outfile


def ogr_buffer(geom, radius, out_file, srs=None):
    """
    For each geometry in the input, this method create a buffer and store it
    in a vetorial file
    
    Accepts files or lists with geom objects as inputs
    """
    
    import os
    from osgeo                     import ogr
    from glass.g.prj               import def_prj
    from glass.g.prop              import drv_name
    from glass.g.prop.prj          import get_sref_from_epsg
    from glass.g.gp.prox.bfing.obj import draw_buffer
    
    # Create output
    buffer_shp = ogr.GetDriverByName(
        drv_name(out_file)).CreateDataSource(out_file)
    
    buffer_lyr = buffer_shp.CreateLayer(
        os.path.splitext(os.path.basename(out_file))[0],
        get_sref_from_epsg(srs) if srs else None,
        geom_type=ogr.wkbPolygon
    )
    
    featDefn = buffer_lyr.GetLayerDefn()
    
    if type(geom) == list:
        for g in geom:
            feat = ogr.Feature(featDefn)
            feat.SetGeometry(draw_buffer(g, radius))
            
            buffer_lyr.CreateFeature(feat)
            
            feat = None
        
        buffer_shp.Destroy()
    
    elif type(geom) == dict:
        if 'x' in geom and 'y' in geom:
            X='x'; Y='y'
        elif 'X' in geom and 'Y' in geom:
            X='X'; Y='Y'
        else:
            raise ValueError((
                'Your geom dict has invalid keys. '
                'Please use one of the following combinations: '
                'x, y; '
                'X, Y'
            ))
        
        from glass.g.gobj import new_pnt
        
        feat = ogr.Feature(featDefn)
        g = new_pnt(geom[X], geom[Y])
        feat.SetGeometry(draw_buffer(g, radius))
        
        buffer_lyr.CreateFeature(feat)
        
        feat = None
        
        buffer_shp.Destroy()
        
        if srs:
            def_prj(out_file, epsg=srs)
    
    elif type(geom) == str:
        # Check if the input is a file
        if os.path.exists(geom):
            inShp = ogr.GetDriverByName(drv_name(geom)).Open(geom, 0)
            
            lyr = inShp.GetLayer()
            for f in lyr:
                g = f.GetGeometryRef()
                
                feat = ogr.Feature(featDefn)
                feat.SetGeometry(draw_buffer(g, radius))
                
                buffer_lyr.CreateFeature(feat)
                
                feat = None
            
            buffer_shp.Destroy()
            inShp.Destroy()
            
            if srs:
                def_prj(out_file, epsg=srs)
            else:
                def_prj(out_file, template=geom)
            
        else:
            raise ValueError('The given path does not exist')
    
    else:
        raise ValueError('Your geom input is not valid')
    
    return out_file

