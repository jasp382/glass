"""
Proximity Tools
"""


def grs_near(fromShp, toShp, nearCatCol='tocat', nearDistCol="todistance",
         maxDist=-1, as_cmd=None):
    """
    v.distance - Finds the nearest element in vector map 'to'
    for elements in vector map 'from'.
    """
    
    from glass.tbl.col import add_fields
    
    add_fields(fromShp, {
        nearCatCol : 'INTEGER', nearDistCol: 'DOUBLE PRECISION'
    }, api="grass" if as_cmd else "pygrass")
    
    if not as_cmd:
        import grass.script as grass
        
        grass.run_command(
            "v.distance", _from=fromShp, to=toShp,
            upload='cat,dist',
            column='{},{}'.format(nearCatCol, nearDistCol),
            dmax=maxDist
        )
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.distance from={} to={} upload=cat,dist "
            "column={},{} dmax={}"
        ).format(fromShp, toShp, nearCatCol, nearDistCol, maxDist))


def pnts_dist(inShp, nearShp, outTbl, maxDist=None):
    """
    Computes distances between pairs of points.
    """
    
    from glass.pys import execmd
    
    c = (
        "saga_cmd shapes_points 3 -POINTS {} -NEAR {} -DISTANCES {} "
        "-FORMAT 1{}"
    ).format(
        inShp, nearShp, outTbl,
        "" if not maxDist else " -MAX_DIST {}".format(maxDist)
    )
    
    outcmd = execmd(c)
    
    return outTbl


def connect_lines_to_near_lines(inLines, nearLines, outLines,
                                tollerance=1000):
    """
    Connect all vertex in a line to the nearest vertex of the nearest
    line
    """

    from osgeo                     import ogr
    from glass.pys.oss             import fprop
    from glass.prop              import drv_name
    from glass.prop.feat         import get_gtype
    from glass.gp.prox.bfing.obj import draw_buffer

    # Check Geometries
    inLinesGeom   = get_gtype(  inLines, gisApi='ogr')
    nearLinesGeom = get_gtype(nearLines, gisApi='ogr')

    if inLinesGeom != 'LINESTRING' or \
       nearLinesGeom != 'LINESTRING':
        raise ValueError('This method supports only LINESTRINGS')

    # Open inLines
    shpLines = ogr.GetDriverByName(
        drv_name(inLines)).Open(inLines)

    # Get Layer
    lyrLines = shpLines.GetLayer()

    # Open near
    shpNear = ogr.GetDriverByName(
        drv_name(nearLines)).Open(nearLines)

    # Create Output
    outSrc = ogr.GetDriverByName(
        drv_name(outLines)).CreateDataSource(outLines)

    outLyr = outSrc.CreateLayer(
        fprop(outLines, 'fn'), geom_type=ogr.wkbLineString)

    lineDefn = outLyr.GetLayerDefn()

    # For each point in 'inLines', find the near point on the
    # the 'nearLines' layer
    nearPoints = {}
    for feat in lyrLines:
        FID = feat.GetFID()
        # Get Geometry
        geom = feat.GetGeometryRef()

        # Get points
        nrPnt = geom.GetPointCount()
        for p in range(nrPnt):
            x, y, z = geom.GetPoint(p)
            pnt = ogr.Geometry(ogr.wkbPoint)
            pnt.AddPoint(x, y)

            # Get point buffer
            bufPnt = draw_buffer(pnt, tollerance)

            # Apply a spatial filter based on the buffer
            # to restrict the nearLines Layer
            lyrNear = shpNear.GetLayer()

            lyrNear.SetSpatialFilter(bufPnt)

            # For line in the filtered 'nearLyr'
            # Find the closest point
            dist = 0
            for __feat in lyrNear:
                __FID = __feat.GetFID()
                __geom = __feat.GetGeometryRef()

                points = __geom.GetPointCount()

                for _p in range(points):
                    _x, _y, _z = __geom.GetPoint(_p)

                    distance = ((x - _x)**2 + (y - _y)**2)**0.5

                    if not dist:
                        dist = [distance, _x, _y]

                    else:
                        if distance < dist[0]:
                            dist = [distance, _x, _y]

            # Write a new line
            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint(x, y)
            line.AddPoint(dist[1], dist[2])

            new_feature = ogr.Feature(lineDefn)
            new_feature.SetGeometry(line)

            outLyr.CreateFeature(new_feature)

            new_feature.Destroy()

            del lyrNear

    outSrc.Destroy()
    shpLines.Destroy()
    shpNear.Destroy()

    return outLines


def connect_points_to_near_line_vertex(inPnt, nearLines, outLines,
                                       tollerance=1000):
    """
    Connect points to the nearest vertex of the nearest
    line
    """

    from osgeo             import ogr
    from glass.prop      import drv_name
    from glass.prop.feat import get_gtype
    from glass.pys.oss     import fprop
    from glass.gp.prox.bfing.obj import draw_buffer

    # Check Geometries
    inPntGeom     = get_gtype(    inPnt, gisApi='ogr')
    nearLinesGeom = get_gtype(nearLines, gisApi='ogr')

    if inPntGeom != 'POINT' or \
       nearLinesGeom != 'LINESTRING':
        raise ValueError('This method supports only LINESTRINGS')

    # Open inLines
    shpPnt = ogr.GetDriverByName(drv_name(inPnt)).Open(inPnt)

    # Get Layer
    lyrPnt = shpPnt.GetLayer()

    # Open near
    shpNear = ogr.GetDriverByName(drv_name(nearLines)).Open(nearLines)

    # Create Output
    outSrc = ogr.GetDriverByName(drv_name(outLines)).CreateDataSource(outLines)

    outLyr = outSrc.CreateLayer(
        fprop(outLines, 'fn'),
        geom_type=ogr.wkbLineString
    )

    lineDefn = outLyr.GetLayerDefn()

    # For each point in 'inLines', find the near point on the
    # the 'nearLines' layer
    for feat in lyrPnt:
        FID = feat.GetFID()
        # Get Geometry
        pnt = feat.GetGeometryRef()

        x, y = pnt.GetX(), pnt.GetY()

        # Get point buffer
        bufPnt = draw_buffer(pnt, tollerance)

        # Apply a spatial filter based on the buffer
        # to restrict the nearLines Layer
        lyrNear = shpNear.GetLayer()

        lyrNear.SetSpatialFilter(bufPnt)

        # For line in the filtered 'nearLyr'
        # Find the closest point
        dist = 0
        for __feat in lyrNear:
            __FID = __feat.GetFID()
            __geom = __feat.GetGeometryRef()

            points = __geom.GetPointCount()

            for _p in range(points):
                _x, _y, _z = __geom.GetPoint(_p)

                distance = ((x - _x)**2 + (y - _y)**2)**0.5

                if not dist:
                    dist = [distance, _x, _y]

                else:
                    if distance < dist[0]:
                        dist = [distance, _x, _y]

        # Write a new line
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(x, y)
        line.AddPoint(dist[1], dist[2])

        new_feature = ogr.Feature(lineDefn)
        new_feature.SetGeometry(line)

        outLyr.CreateFeature(new_feature)

        new_feature.Destroy()

        del lyrNear

    outSrc.Destroy()
    shpPnt.Destroy()
    shpNear.Destroy()

    return outLines


def connect_points_to_near_line(inPnt, nearLines, outLines,
                                tollerance=1000, nearLinesWpnt=None):
    """
    Connect all points to the nearest line in the perpendicular
    """

    import os
    from osgeo             import ogr
    from shapely.geometry  import LineString, Point
    from glass.prop      import drv_name
    from glass.prop.feat import get_gtype
    from glass.pys.oss     import fprop
    from glass.gp.prox.bfing.obj import draw_buffer

    # Check Geometries
    inPntGeom     = get_gtype(inPnt, gisApi='ogr')
    nearLinesGeom = get_gtype(nearLines, gisApi='ogr')

    if inPntGeom != 'POINT' or \
       nearLinesGeom != 'LINESTRING':
        raise ValueError('This method supports only LINESTRINGS')

    # Open inLines
    shpPnt = ogr.GetDriverByName(drv_name(inPnt)).Open(inPnt)

    # Get Layer
    lyrPnt = shpPnt.GetLayer()

    # Open near
    shpNear = ogr.GetDriverByName(drv_name(nearLines)).Open(nearLines)

    # Create Output
    outSrc = ogr.GetDriverByName(drv_name(outLines)).CreateDataSource(outLines)

    outLyr = outSrc.CreateLayer(
        os.path.splitext(os.path.basename(outLines))[0],
        geom_type=ogr.wkbLineString
    )

    if nearLinesWpnt:
        newPointsInLines = {}

    lineDefn = outLyr.GetLayerDefn()
    # For each point in 'inLines', find the near point on the
    # the 'nearLines' layer
    for feat in lyrPnt:
        FID = feat.GetFID()
        # Get Geometry
        pnt = feat.GetGeometryRef()

        x, y = pnt.GetX(), pnt.GetY()

        # Get point buffer
        bufPnt = draw_buffer(pnt, tollerance)

        # Apply a spatial filter based on the buffer
        # to restrict the nearLines Layer
        lyrNear = shpNear.GetLayer()

        lyrNear.SetSpatialFilter(bufPnt)

        # For line in the filtered 'nearLyr'
        # Find point in the perpendicular
        dist = 0
        for __feat in lyrNear:
            __FID = __feat.GetFID()
            __geom = __feat.GetGeometryRef()

            points = __geom.GetPointCount()

            for _p in range(points - 1):
                # Get line segment
                x1, y1, z1 = __geom.GetPoint(_p)
                x2, y2, z2 = __geom.GetPoint(_p + 1)

                # Create Shapely Geometries
                lnh = LineString([(x1, y1), (x2, y2)])

                pnt = Point(x, y)

                # Get distance between point and line
                # Get near point of the line
                d = pnt.distance(lnh)
                npnt = lnh.interpolate(lnh.project(pnt))

                if not dist:
                    dist = [d, npnt.x, npnt.y]
                    LINE_FID = __FID

                else:
                    if d < dist[0]:
                        dist = [d, npnt.x, npnt.y]
                        LINE_FID = __FID

        # Write a new line
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint(x, y)
        line.AddPoint(dist[1], dist[2])

        new_feature = ogr.Feature(lineDefn)
        new_feature.SetGeometry(line)

        outLyr.CreateFeature(new_feature)

        new_feature.Destroy()

        if nearLinesWpnt:
            if LINE_FID not in newPointsInLines:
                newPointsInLines[LINE_FID] = [Point(dist[1], dist[2])]
            else:
                newPointsInLines[LINE_FID].append(Point(dist[1], dist[2]))

        del lyrNear

    outSrc.Destroy()
    shpPnt.Destroy()
    shpNear.Destroy()

    if nearLinesWpnt:
        from glass.lyr.fld import copy_flds
        from shapely.ops          import split as lnhSplit
        
        shpNear = ogr.GetDriverByName(
                drv_name(nearLines)).Open(nearLines)
        
        updateLines = ogr.GetDriverByName(
            drv_name(nearLinesWpnt)).CreateDataSource(nearLinesWpnt)

        upLnhLyr = updateLines.CreateLayer(
            fprop(nearLinesWpnt, 'fn'),
            geom_type=ogr.wkbLineString
        )

        # Create shpNear Layer Again
        lyrNear = shpNear.GetLayer()

        # Copy fields
        copy_flds(lyrNear, upLnhLyr)

        # Out lyr definition
        upDefn = upLnhLyr.GetLayerDefn()
        for feat in lyrNear:
            LINE_FID = feat.GetFID()

            geom = feat.GetGeometryRef()

            new_feature = ogr.Feature(upDefn)

            if LINE_FID not in newPointsInLines:
                # Copy line to updateLines layer
                new_feature.SetGeometry(geom)

            else:
                # Copy to Shapely Line String
                points = geom.GetPointCount()

                lstPnt = []
                for _p in range(points):
                    x1, y1, z1 = geom.GetPoint(_p)
                    lstPnt.append((x1, y1))

                shplyLnh = LineString(lstPnt)
                # For new point:
                # Line split and reconstruction
                for pnt in newPointsInLines[LINE_FID]:
                    try:
                        splitted = lnhSplit(shplyLnh, pnt)
                    except:
                        shpTstL = ogr.GetDriverByName(
                            "ESRI Shapefile").CreateDataSource(r'D:\gis\xyz\lnht.shp')
                        
                        shpL = shpTstL.CreateLayer(
                            'lnht',
                            geom_type=ogr.wkbLineString
                        )
                        
                        shpTstP = ogr.GetDriverByName(
                            "ESRI Shapefile").CreateDataSource(r'D:\gis\xyz\pntt.shp')
                                                
                        shpP = shpTstL.CreateLayer(
                            'pntt',
                            geom_type=ogr.wkbPoint
                        )
                        
                        defnL = shpL.GetLayerDefn()
                        defnP = shpP.GetLayerDefn()
                        
                        featL = ogr.Feature(defnL)
                        featP = ogr.Feature(defnP)
                        
                        geomL = ogr.Geometry(ogr.wkbLineString)
                        for i in list(shplyLnh.coords):
                            geomL.AddPoint(i[0], i[1])
                        geomP = ogr.Geometry(ogr.wkbPoint)
                        
                        geomP.AddPoint(list(pnt.coords)[0][0], list(pnt.coords)[0][1])
                        
                        featL.SetGeometry(geomL)
                        featP.SetGeometry(geomP)
                        
                        shpL.CreateFeature(featL)
                        shpP.CreateFeature(featP)
                        
                        shpTstL.Destroy()
                        shpTstP.Destroy()
                        
                        return pnt, shplyLnh

                    c = 0
                    for l in splitted:
                        if not c:
                            newLnh = list(l.coords)
                        else:
                            newlnh += list(l.coords)[1:]
                        c += 1

                    shplyLnh = LineString(newLnh)

                # Finally copy line to updateLines Layer
                gLine = ogr.Geometry(ogr.wkbLineString)
                for __pnt in list(shplyLnh.coords):
                    gLine.AddPoint(__pnt[0], __pnt[1])

            for i in range(0, upDefn.GetFieldCount()):
                new_feature.SetField(
                    upDefn.GetFieldDefn(i).GetNameRef(),
                    feat.GetField(i)
                )

            upLnhLyr.CreateFeature(new_feature)

            new_feature.Destroy()

    shpNear.Destroy()

    return outLines
