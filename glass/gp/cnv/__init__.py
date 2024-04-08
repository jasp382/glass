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


def feat_to_polygons(inShp, outShp, api='saga', db=None):
    """
    Features to Polygons
    
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
            f"saga_cmd shapes_polygons 3 -POLYGONS {outShp} "
            f"LINES {inShp} -SINGLE 1 -MERGE 1"
        ))
    
    elif api == 'grass' or api == 'pygrass':
        # Do it using GRASS GIS
        
        import os
        from glass.wenv.grs import grass_session
        from glass.pys.oss  import fprop
        
        # Create GRASS GIS Session
        wk = os.path.dirname(outShp)
        lo = fprop(outShp, 'fn', forceLower=True)
        
        gs = grass_session(wk, loc=lo, srs=inShp)
        
        # Import Packages
        from glass.it.shp import shp_to_grs, grs_to_shp
        from glass.gp.cnv.grs import line_to_polyline, geomtype_to_geomtype, boundary_to_areas
        
        # Send data to GRASS GIS
        lnh_shp = shp_to_grs(inShp, asCMD=True if api == 'grass' else None)
        
        # Build Polylines
        pol_lnh = line_to_polyline(
            lnh_shp, "polylines",
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
        from glass.pys.oss    import fprop
        from glass.sql.db     import create_pgdb
        from glass.it.db      import shp_to_psql
        from glass.it.shp     import dbtbl_to_shp
        from glass.gp.cnv.sql import feat_to_polg
        from glass.prop.prj   import shp_epsg
        from glass.sql.q      import exec_write_q
        
        # Create DB
        if not db:
            db = create_pgdb(fprop(inShp, 'fn', forceLower=True))
        
        else:
            from glass.prop.sql import db_exists
            isDB = db_exists(db)
            
            if not isDB:
                create_pgdb(db, api='psql')
        
        # Send data to DB
        in_tbl = shp_to_psql(db, inShp, api="ogr2ogr")

        # Create an index to speed things up
        exec_write_q(db, [(
           f"DROP INDEX IF EXISTS {in_tbl}_geom_idx"
        ), (
            f"CREATE INDEX {in_tbl}_geometry_idx "
            f"ON {in_tbl} USING spgist (geom)"
        )], api='psql')
        
        # Get Result
        result = feat_to_polg(db, in_tbl, "geom", ogeom="geom", out=None)
        
        # Export Result
        outshp = dbtbl_to_shp(
            db, result, "geom", outShp, api='ogr2ogr',
            tableIsQuery=True,
            epsg=shp_epsg(inShp)
        )
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outShp


def feat_to_pnt(inShp, outPnt, epsg=None, geomcol='geometry', api='pandas'):
    """
    Get Centroid from each line in a PolyLine Feature Class
    """
    
    import os
    from osgeo  import ogr

    from glass.prop.df  import drv_name
    from glass.lyr.fld  import copy_flds
    from glass.prop.shp import lst_shpcols
    
    # TODO: check if geometry is correct
    
    # Open data
    polyData = ogr.GetDriverByName(
        drv_name(outPnt)).Open(inShp)
    
    polyLyr  = polyData.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.prop.prj import shp_ref
        srs = shp_ref(polyLyr)
    
    else:
        from glass.prop.prj import sref_from_epsg
        srs = sref_from_epsg(epsg)
    
    # Create output
    pntData = ogr.GetDriverByName(
        drv_name(outPnt)).CreateDataSource(outPnt)
    
    pntLyr = pntData.CreateLayer(
        os.path.splitext(os.path.basename(outPnt))[0],
        srs, geom_type=ogr.wkbPoint
    )
    
    # Copy fields from input to output
    fields = lst_shpcols(polyLyr)
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


def pnts_to_boundary(pntShp, outBound, distMeters):
    """
    Create a boundary from Point using a tolerance in meters
    """
    
    from osgeo          import ogr
    from glass.pys.oss  import fprop
    from glass.prop.df  import drv_name
    from glass.gobj     import new_pnt
    from glass.prop.prj import shp_ref
    
    SRS = shp_ref(pntShp)
    
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


def polyline_to_points(inShp, outShp, attr=None, epsg=None):
    """
    Polyline vertex to Points
    
    TODO: See if works with Polygons
    """
    
    import os
    from osgeo         import ogr
    from glass.prop.df import drv_name
    from glass.lyr.fld import copy_flds
    
    # Open Input
    polyData = ogr.GetDriverByName(drv_name(inShp)).Open(inShp)
    
    polyLyr = polyData.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.prop.prj import shp_ref
        srs = shp_ref(polyLyr)
    
    else:
        from glass.prop.prj import sref_from_epsg
        srs = sref_from_epsg(epsg)
    
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
    
    import os
    from osgeo import ogr
    from glass.prop.df  import drv_name
    from glass.prop.col import ogr_list_fields_defn
    from glass.lyr.fld  import fields_to_lyr
    
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
        from glass.prop.prj import shp_ref
        srs = shp_ref(points)
    
    else:
        from glass.prop.prj import sref_from_epsg
        srs = sref_from_epsg(epsg)
    
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

