"""
Python data to SHP
"""

def df_to_shp(indf, outShp, layername=None):
    """
    Pandas Dataframe to Geospatial file
    """

    from glass.prop.df import drv_name

    drv = drv_name(outShp)

    if drv == 'GPKG' and layername:
        indf.to_file(outShp, driver=drv, layer=layername)
    
    else:
        indf.to_file(outShp)
    
    return outShp


def obj_to_shp(dd, geomkey, srs, outshp, lyrname=None, iswkt=None, cols=None):
    """
    Write geoobject in shapefile
    """

    if not iswkt:
        from glass.it.pd import df_to_geodf as obj_to_geodf
    
    else:
        from glass.it.pd import obj_to_geodf

        if cols and geomkey not in cols:
            cols.append(geomkey)
    
    geodf = obj_to_geodf(dd, geomkey, srs, cols=cols)
    
    return df_to_shp(geodf, outshp, layername=lyrname)


def coords_to_boundshp(topLeft, lowerRight, epsg, outshp,
                       outEpsg=None, fields=None):
    """
    Top Left and Lower Right to Boundary
    """
    
    from osgeo          import ogr
    from glass.prop.df  import drv_name
    from glass.prop.prj import sref_from_epsg
    from glass.pys.oss  import fprop
    from glass.pys      import obj_to_lst
    from glass.gp.cnv   import coords_to_boundary

    toplefts = obj_to_lst(topLeft)
    lrights  = obj_to_lst(lowerRight)

    if len(toplefts) != len(lrights):
        raise ValueError(
            'topLeft and lowerRight must have the same length'
        )
    
    # Get fields to create
    if fields:
        fields = obj_to_lst(fields)
        allcols = []
        for a in fields:
            for k in a:
                if k not in allcols:
                    allcols.append(k)
    else:
        allcols=None
    
    # Create outShapefile if a path is given
    shp = ogr.GetDriverByName(
        drv_name(outshp)).CreateDataSource(outshp)
    
    SRS_OBJ = sref_from_epsg(epsg) if not outEpsg else \
        sref_from_epsg(outEpsg)
    
    lyr = shp.CreateLayer(fprop(
        outshp, 'fn'), SRS_OBJ, geom_type=ogr.wkbPolygon
    )

    # Create fields
    if fields:
        for f in allcols:
            lyr.CreateField(ogr.FieldDefn(f, ogr.OFTString))

    outDefn = lyr.GetLayerDefn()

    for i in range(len(toplefts)):
        # Get boundary geometry
        polygon = coords_to_boundary(
            toplefts[i], lrights[i],
            epsg, outEpsg=outEpsg
        )
    
        feat = ogr.Feature(outDefn)
    
        feat.SetGeometry(polygon)
        if fields:
            for d in fields:
                ks = list(d.keys())
                for c in allcols:
                    if c not in ks:
                        feat.SetField(c, '')
                    else:
                        feat.SetField(c, d[c])

        lyr.CreateFeature(feat)
    
        feat.Destroy()
    shp.Destroy()
    
    return outshp


def rstext_to_shp(inRst, outShp, epsg=None):
    """
    Raster Extent to Feature Class
    """
    
    from glass.prop.rst import rst_ext
    
    # Get Raster Extent
    left, right, bottom, top = rst_ext(inRst)
    
    # Get EPSG
    if not epsg:
        from glass.prop.prj import rst_epsg
        
        epsg = rst_epsg(inRst)
    
    # Create Boundary
    return coords_to_boundshp((left, top), (right, bottom), epsg, outShp)

