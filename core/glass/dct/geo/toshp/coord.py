"""
Numerical to Shape
"""

def coords_to_boundshp(topLeft, lowerRight, epsg, outshp,
                       outEpsg=None):
    """
    Top Left and Lower Right to Boundary
    """
    
    import os; from osgeo   import ogr
    from glass.geo.prop.df  import drv_name
    from glass.geo.prop.prj import get_sref_from_epsg
    from glass.pys.oss      import fprop
    from glass.geo.obj.to   import coords_to_boundary

    # Get boundary geometry
    polygon = coords_to_boundary(topLeft, lowerRight, epsg, outEpsg=outEpsg)
    
    # Create outShapefile if a path is given
    shp = ogr.GetDriverByName(
        drv_name(outshp)).CreateDataSource(outshp)
    
    SRS_OBJ = get_sref_from_epsg(epsg) if not outEpsg else \
        get_sref_from_epsg(outEpsg)
    lyr = shp.CreateLayer(fprop(
        outshp, 'fn'), SRS_OBJ, geom_type=ogr.wkbPolygon
    )
    
    outDefn = lyr.GetLayerDefn()
    
    feat = ogr.Feature(outDefn)
    
    feat.SetGeometry(polygon)
    lyr.CreateFeature(feat)
    
    feat.Destroy()
    shp.Destroy()
    
    return outshp


"""
Extent to Shape
"""

def shpext_to_boundshp(inShp, outShp, epsg=None):
    """
    Read one feature class extent and create a boundary with that
    extent
    
    The outFile could be a Feature Class or one Raster Dataset
    """
    
    import os
    from osgeo             import ogr
    from glass.geo.prop.df import drv_name
    from glass.pys.oss     import fprop
    from glass.geo.obj.g   import new_pnt
    from glass.geo.obj.to  import shpext_to_boundary
    
    # Get SRS for the output
    if not epsg:
        from glass.geo.prop.prj import get_shp_sref
        
        srs = get_shp_sref(inShp)
    
    else:
        from glass.geo.prop.prj import get_sref_from_epsg
        
        srs= get_sref_from_epsg(epsg)
    
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


def pnts_to_boundary(pntShp, outBound, distMeters):
    """
    Create a boundary from Point using a tolerance in meters
    """
    
    from osgeo              import ogr
    from glass.pys.oss      import fprop
    from glass.geo.prop.df  import drv_name
    from glass.geo.obj.g    import new_pnt
    from glass.geo.prop.prj import get_shp_sref
    
    SRS = get_shp_sref(pntShp)
    
    shp = ogr.GetDriverByName(drv_name(pntShp)).Open(pntShp)
    lyr = shp.GetLayer()
    
    outShp = ogr.GetDriverByName(drv_name(outBound)).CreateDataSource(outBound)
    outLyr = outShp.CreateLayer(
        fprop(outBound, 'fn', forceLower=True), SRS,
        geom_type=ogr.wkbPolygon
    )
    
    outDefn = outLyr.GetLayerDefn()
    
    for feat in lyr:
        __feat = ogr.Feature(outDefn)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        
        geom = feat.GetGeometryRef()
        X, Y = geom.GetX(), geom.GetY()
        
        boundary_points = [
            new_pnt(X - distMeters, Y + distMeters), # Topleft
            new_pnt(X + distMeters, Y + distMeters), # TopRight
            new_pnt(X + distMeters, Y - distMeters), # Lower Right
            new_pnt(X - distMeters, Y - distMeters), # Lower Left
            new_pnt(X - distMeters, Y + distMeters)
        ]
        
        for pnt in boundary_points:
            ring.AddPoint(pnt.GetX(), pnt.GetY())
        
        polygon = ogr.Geometry(ogr.wkbPolygon)
        polygon.AddGeometry(ring)
        
        __feat.SetGeometry(polygon)
        
        outLyr.CreateFeature(__feat)
        
        feat.Destroy()
        
        __feat  = None
        ring    = None
        polygon = None
    
    shp.Destroy()
    outShp.Destroy()
    
    return outBound


def rstext_to_shp(inRst, outShp, epsg=None):
    """
    Raster Extent to Feature Class
    """
    
    from glass.geo.prop.rst import rst_ext
    
    # Get Raster Extent
    left, right, bottom, top = rst_ext(inRst)
    
    # Get EPSG
    if not epsg:
        from glass.geo.prop.prj import get_rst_epsg
        
        epsg = get_rst_epsg(inRst)
    
    # Create Boundary
    return coords_to_boundshp((left, top), (right, bottom), epsg, outShp)

