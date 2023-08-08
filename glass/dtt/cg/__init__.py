"""
Change Geometry types
"""


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


def feat_to_pnt(inShp, outPnt, epsg=None):
    """
    Get Centroid from each line in a PolyLine Feature Class
    """
    
    import os
    from osgeo  import ogr
    from glass.prop.df   import drv_name
    from glass.lyr.fld   import copy_flds
    from glass.prop.feat import lst_fld
    
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


def boundary_to_areas(inShp, outShp, useCMD=None):
    """
    v.centroids - Adds missing centroids to closed boundaries. 
    
    GRASS defines vector areas as composite entities consisting of a set of
    closed boundaries and a centroid. The attribute information associated with
    that area is linked to the centroid. The v.centroids module adds centroids
    to closed boundaries in the input file and assigns a category number to them.
    The starting value as well as the increment size may be set using optional
    parameters.
    
    Multiple attributes may be linked to a single vector entity through numbered
    fields referred to as layers. Refer to v.category for more details, as
    v.centroids is simply a frontend to that module.
    
    The boundary itself is often stored without any category reference as it can
    mark the border between two adjacent areas. Thus it would be ambiguous as to
    which feature the attribute would belong. In some cases it may, for example,
    represent a road between two parcels of land. In this case it is entirely
    appropriate for the boundary to contain category information. 
    """
    
    if not useCMD:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.centroids", input=inShp, output=outShp,
            overwrite=True, quiet=True, run_=False
        )
        
        m()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            "v.centroids input={} output={} --overwrite --quiet"
        ).format(inShp, outShp))
    
    return outShp


def geomtype_to_geomtype(inShp, outShp, fm_type, to_type, cmd=None):
    """
    v.type - Changes type of vector features.
    
    v.type changes the type of geometry primitives.
    """
    
    if not cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.type", input=inShp, output=outShp, from_type=fm_type,
            to_type=to_type, overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            "v.type input={} output={} from_type={} to_type={} "
            "--overwrite --quiet"
        ).format(inShp, outShp, fm_type, to_type))
    
    return outShp


def line_to_polyline(inShp, outShp, asCmd=None):
    """
    v.build.polylines - Builds polylines from lines or boundaries.
    
    v.build.polylines builds polylines from the lines or boundaries in a vector map.
    
    A line is defined by one start node, one end node and any number of vertices
    between the start and end nodes. The shortest possible line consists of only two
    vertices where the coordinates of the start and end nodes are identical to
    those of the two vertices.
    
    v.build.polylines picks a line and from its start node, walks back as long
    as exactly one other line of the same type is connected to this node. Line
    directions are reversed as required, i.e. it does not matter if the next line
    is connected to the current node by its start or end node. Once the start
    line of a polyline is identified, it walks forward and adds all vertices (
    in reverse order if needed) of connected lines to the start line, i.e. the
    start line and connecting lines are reversed as needed. That is, if a line is
    reversed depends on what node is initially picked for building polylines.
    If the direction of lines is important (it's not for boundaries to build
    areas), you have to manually change line directions with either v.edit or
    the wxGUI vector digitizer.
    
    Polylines provide the most appropriate representation of curved lines when
    it is important that nodes serve to define topology rather than geometry.
    Curved lines are usually digitized as polylines, but these are sometimes
    broken into their constituent straight line segments during conversion from
    one data format to another. v.build.polylines can be used to rebuild such
    broken polylines. 
    """
    
    if not asCmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.build.polylines", input=inShp, output=outShp,
            cats='same', overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            "v.build.polylines input={} output={} cats='same' "
            "--overwrite --quiet"
        ).format(inShp, outShp))
    
    return outShp


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
            f"saga_cmd shapes_polygons 3 -POLYGONS {outShp} "
            f"LINES {inShp} -SINGLE 1 -MERGE 1"
        ))
    
    elif api == 'grass' or api == 'pygrass':
        # Do it using GRASS GIS
        
        import os
        from glass.wenv.grs import run_grass
        from glass.pys.oss  import fprop
        
        # Create GRASS GIS Session
        wk = os.path.dirname(outShp)
        lo = fprop(outShp, 'fn', forceLower=True)
        
        gs = run_grass(wk, lo, srs=inShp)
        
        import grass.script.setup as gsetup
        gsetup.init(gs, wk, lo, 'PERMANENT')
        
        # Import Packages
        from glass.it.shp import shp_to_grs, grs_to_shp
        
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
        from glass.sql.db     import create_db
        from glass.it.db      import shp_to_psql
        from glass.it.shp     import dbtbl_to_shp
        from glass.dtt.cg.sql import lnh_to_polg
        from glass.prop.prj   import shp_epsg
        from glass.sql.q      import exec_write_q
        
        # Create DB
        if not db:
            db = create_db(fprop(inShp, 'fn', forceLower=True), api='psql')
        
        else:
            from glass.prop.sql import db_exists
            isDB = db_exists(db)
            
            if not isDB:
                create_db(db, api='psql')
        
        # Send data to DB
        in_tbl = shp_to_psql(db, inShp, api="shp2pgsql")

        # Create an index to speed things up
        exec_write_q(db, [(
           f"DROP INDEX IF EXISTS {in_tbl}_geom_idx"
        ), (
            f"CREATE INDEX {in_tbl}_geometry_idx "
            f"ON {in_tbl} USING spgist (geom)"
        )], api='psql')
        
        # Get Result
        result = lnh_to_polg(db, in_tbl, fprop(
            outShp, 'fn', forceLower=True))
        
        # Export Result
        outshp = dbtbl_to_shp(
            db, result, "geom", outShp, api='psql',
            epsg=shp_epsg(inShp))
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outShp


def feat_vertex_to_pnt(inShp, outPnt, nodes=True):
    """
    Feature Class to a Point Feature Class
    
    v.to.points - Creates points along input lines in new vector map with
    2 layers.
    
    v.to.points creates points along input 2D or 3D lines, boundaries and
    faces. Point features including centroids and kernels are copied from
    input vector map to the output. For details see notes about type parameter.
    
    The output is a vector map with 2 layers. Layer 1 holds the category of
    the input features; all points created along the same line have the same
    category, equal to the category of that line. In layer 2 each point has
    its unique category; other attributes stored in layer 2 are lcat - the
    category of the input line and along - the distance from line's start.
    
    By default only features with category are processed, see layer parameter
    for details.
    """
    
    from grass.pygrass.modules import Module
    
    toPnt = Module(
        "v.to.points", input=inShp,
        output=outPnt,
        use="node" if nodes else "vertex",
        overwrite=True, run_=False,
        quiet=True
    )
    
    toPnt()
    
    return outPnt

