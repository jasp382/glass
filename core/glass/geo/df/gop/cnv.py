"""
Geometric Conversion
"""

def polyline_to_points(inShp, outShp, attr=None, epsg=None):
    """
    Polyline vertex to Points
    
    TODO: See if works with Polygons
    """
    
    import os
    from osgeo import ogr
    from glass.geo.prop.df import drv_name
    from glass.geo.obj.lyr.fld import copy_flds
    
    # Open Input
    polyData = ogr.GetDriverByName(drv_name(inShp)).Open(inShp)
    
    polyLyr = polyData.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.geo.prop.prj import get_shp_sref
        srs = get_shp_sref(polyLyr)
    
    else:
        from glass.geo.prop.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Create Output
    pntData = ogr.GetDriverByName(
        drv_name(outShp)).CreateDataSource(outShp)
    
    pntLyr = pntData.CreateLayer(
        os.path.splitext(os.path.basename(outShp))[0],
        srs, geom_type=ogr.wkbPoint
    )
    
    # Copy fields from input to output
    if attr:
        if attr == 'ALL':
            attr = None
        else:
            attr = [attr] if type(attr) != list else attr
        
        copy_flds(polyLyr, pntLyr, __filter=attr)
    
    # Polyline Vertex to Point Feature Class
    pntLyrDefn = pntLyr.GetLayerDefn()
    for feat in polyLyr:
        geom = feat.GetGeometryRef()
        
        # Get point count
        nrPnt = geom.GetPointCount()
        
        # Add point to a new feature
        for p in range(nrPnt):
            x, y, z = geom.GetPoint(p)
            
            new_point = ogr.Geometry(ogr.wkbPoint)
            new_point.AddPoint(x, y)
            
            new_feature = ogr.Feature(pntLyrDefn)
            new_feature.SetGeometry(new_point)
            
            if attr:
                for at in attr:
                    new_feature.SetField(at, feat.GetField(at))
            
            pntLyr.CreateFeature(new_feature)
            
            new_feature.Destroy()
    
    del pntLyr
    del polyLyr
    pntData.Destroy()
    polyData.Destroy()
    
    return outShp


def polylines_from_points(points, polylines, POLYLINE_COLUMN,
                          ORDER_FIELD=None, epsg=None):
    """
    Create a Polyline Table from a Point Table
    
    A given Point Table:
    FID | POLYLINE_ID | ORDER_FIELD
     0  |    P1       |      1
     1  |    P1       |      2
     2  |    P1       |      3
     3  |    P1       |      4
     4  |    P2       |      1
     5  |    P2       |      2
     6  |    P2       |      3
     7  |    P2       |      4
     
    Will be converted into a new Polyline Table:
    FID | POLYLINE_ID
     0  |    P1
     1  |    P2
     
    In the Point Table, the POLYLINE_ID field identifies the Polyline of that point,
    the ORDER FIELD specifies the position (first point, second point, etc.)
    of the point in the polyline.
    
    If no ORDER field is specified, the points will be assigned to polylines
    by reading order.
    """
    
    import os; from osgeo import ogr
    from glass.geo.prop.df  import drv_name
    from glass.geo.df.prj      import def_prj
    from glass.geo.prop.col import ogr_list_fields_defn
    from glass.geo.obj.lyr.fld   import fields_to_lyr
    
    # TODO: check if geometry is correct
    
    # List all points
    pntSrc = ogr.GetDriverByName(
        drv_name(points)).Open(points)
    pntLyr = pntSrc.GetLayer()
    
    lPnt = {}
    cnt = 0
    for feat in pntLyr:
        # Get Point Geom
        geom = feat.GetGeometryRef()
        # Polyline identification
        polyline = feat.GetField(POLYLINE_COLUMN)
        # Get position in the polyline
        order = feat.GetField(ORDER_FIELD) if ORDER_FIELD else cnt
        
        # Store data
        if polyline not in lPnt.keys():
            lPnt[polyline] = {order: (geom.GetX(), geom.GetY())}
        
        else:
            lPnt[polyline][order] = (geom.GetX(), geom.GetY())
        
        cnt += 1
    
    # Write output
    lineSrc = ogr.GetDriverByName(
        drv_name(polylines)).CreateDataSource(polylines)
    
    if not epsg:
        from glass.geo.prop.prj import get_shp_sref
        srs = get_shp_sref(points)
    
    else:
        from glass.geo.prop.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    lineLyr = lineSrc.CreateLayer(
        os.path.splitext(os.path.basename(polylines))[0],
        srs, geom_type=ogr.wkbLineString
    )
    
    # Create polyline id field
    fields_types = ogr_list_fields_defn(pntLyr)
    fields_to_lyr(
        lineLyr, {POLYLINE_COLUMN : list(fields_types[POLYLINE_COLUMN].keys())[0]}
    )
    
    polLnhDefns = lineLyr.GetLayerDefn()
    # Write lines
    for polyline in lPnt:
        new_feature = ogr.Feature(polLnhDefns)
        
        lnh = ogr.Geometry(ogr.wkbLineString)
        
        pnt_order = list(lPnt[polyline].keys())
        pnt_order.sort()
        
        for p in pnt_order:
            lnh.AddPoint(lPnt[polyline][p][0], lPnt[polyline][p][1])
        
        new_feature.SetField(POLYLINE_COLUMN, polyline)
        new_feature.SetGeometry(lnh)
        
        lineLyr.CreateFeature(new_feature)
        
        new_feature = None
    
    pntSrc.Destroy()
    lineSrc.Destroy()
    
    return polylines


def feat_to_pnt(inShp, outPnt, epsg=None):
    """
    Get Centroid from each line in a PolyLine Feature Class
    """
    
    import os; from osgeo       import ogr
    from glass.geo.prop.df   import drv_name
    from glass.geo.obj.lyr.fld   import copy_flds
    from glass.geo.prop.feat import lst_fld
    
    # TODO: check if geometry is correct
    
    # Open data
    polyData = ogr.GetDriverByName(
        drv_name(outPnt)).Open(inShp)
    
    polyLyr  = polyData.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.geo.prop.prj import get_shp_sref
        srs = get_shp_sref(polyLyr)
    
    else:
        from glass.geo.prop.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Create output
    pntData = ogr.GetDriverByName(
        drv_name(outPnt)).CreateDataSource(outPnt)
    
    pntLyr = pntData.CreateLayer(
        os.path.splitext(os.path.basename(outPnt))[0],
        srs, geom_type=ogr.wkbPoint
    )
    
    # Copy fields from input to output
    fields = lst_fld(polyLyr)
    copy_flds(polyLyr, pntLyr)
    
    pntLyrDefn = pntLyr.GetLayerDefn()
    for feat in polyLyr:
        geom = feat.GetGeometryRef()
        
        pnt = geom.Centroid()
        
        new_feat = ogr.Feature(pntLyrDefn)
        new_feat.SetGeometry(pnt)
        
        for fld in fields:
            new_feat.SetField(fld, feat.GetField(fld))
        
        pntLyr.CreateFeature(new_feat)
        
        new_feat.Destroy()
    
    del pntLyr
    del polyLyr
    pntData.Destroy()
    polyData.Destroy()
    
    return outPnt


def lnh_to_polygons(inShp, outShp, api='saga', db=None):
    """
    Line to Polygons
    
    API's Available:
    * saga;
    * grass;
    * pygrass;
    * psql;
    """
    
    if api == 'saga':
        """
        http://www.saga-gis.org/saga_tool_doc/7.0.0/shapes_polygons_3.html
        
        Converts lines to polygons. Line arcs are closed to polygons simply
        by connecting the last point with the first. Optionally parts of
        polylines can be merged into one polygon optionally. 
        """
        
        from glass.pys  import execmd
        
        rcmd = execmd((
            "saga_cmd shapes_polygons 3 -POLYGONS {} "
            "LINES {} -SINGLE 1 -MERGE 1"
        ).format(outShp, inShp))
    
    elif api == 'grass' or api == 'pygrass':
        # Do it using GRASS GIS
        
        import os
        from glass.geo.wenv.grs import run_grass
        from glass.pys.oss      import fprop
        
        # Create GRASS GIS Session
        wk = os.path.dirname(outShp)
        lo = fprop(outShp, 'fn', forceLower=True)
        
        gs = run_grass(wk, lo, srs=inShp)
        
        import grass.script as grass
        import grass.script.setup as gsetup
        gsetup.init(gs, wk, lo, 'PERMANENT')
        
        # Import Packages
        from glass.dct.geo.toshp.cff  import shp_to_grs, grs_to_shp
        from glass.dct.geo.toshp.cgeo import line_to_polyline
        from glass.dct.geo.toshp.cgeo import geomtype_to_geomtype
        from glass.dct.geo.toshp.cgeo import boundary_to_areas
        
        # Send data to GRASS GIS
        lnh_shp = shp_to_grs(inShp, fprop(
            inShp, 'fn', forceLower=True
        ), asCMD=True if api == 'grass' else None)
        
        # Build Polylines
        pol_lnh = line_to_polyline(lnh_shp, "polylines",
                                   asCmd=True if api == 'grass' else None)
        
        # Polyline to boundary
        bound = geomtype_to_geomtype(pol_lnh, 'bound_shp', 'line', 'boundary',
                                     cmd=True if api == 'grass' else None)
        
        # Boundary to Area
        areas_shp = boundary_to_areas(bound, lo,
                                      useCMD=True if api == 'grass' else None)
        
        # Export data
        outShp = grs_to_shp(areas_shp, outShp, 'area',
                            asCMD=True if api == 'grass' else None)
    
    elif api == 'psql':
        """ Do it using PostGIS """
        from glass.pys.oss          import fprop
        from glass.sql.db           import create_db
        from glass.dct.gql          import shp_to_psql
        from glass.dct.geo.toshp.db import dbtbl_to_shp
        from glass.geo.gql.cnv      import lnh_to_polg
        from glass.geo.prop.prj     import get_epsg_shp
        
        # Create DB
        if not db:
            db = create_db(fprop(inShp, 'fn', forceLower=True), api='psql')
        
        else:
            from glass.sql.prop import db_exists
            isDB = db_exists(db)
            
            if not isDB:
                create_db(db, api='psql')
        
        # Send data to DB
        in_tbl = shp_to_psql(db, inShp, api="shp2pgsql")
        
        # Get Result
        result = lnh_to_polg(db, in_tbl, fprop(
            outShp, 'fn', forceLower=True))
        
        # Export Result
        outshp = dbtbl_to_shp(
            db, result, "geom", outShp, api='psql',
            epsg=get_epsg_shp(inShp))
    
    else:
        raise ValueError("API {} is not available".format(api))
    
    return outShp

