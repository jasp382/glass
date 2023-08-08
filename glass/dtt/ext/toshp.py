"""
Numerical to Shape
"""

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


def rstext_to_shp(inRst, outShp, epsg=None):
    """
    Raster Extent to Feature Class
    """
    
    from glass.prop.rst import rst_ext
    from glass.prop.prj import rst_epsg
    
    # Get Raster Extent
    left, right, bottom, top = rst_ext(inRst)
    
    # Get EPSG
    if not epsg:
        epsg = rst_epsg(inRst)
    
    # Create Boundary
    return coords_to_boundshp((left, top), (right, bottom), epsg, outShp)


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

