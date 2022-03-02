"""
Network Methods combining some GIS Tools
"""

import arcpy


def service_area_as_sup_cst(networkDataset, rdvName, extentLyr, originsLyr, output,
                            epsg=3763, REF_DISTANCE=3000, NR_INTERVALS=20):
    """
    Create a Cost Distance Surface using Service Area Tool
    
    Same result of the Cost Distance tool but using Service Area Tool
    
    Supported by Google Maps API
    
    PROBLEM: REF_DISTANCE should be greater if the extent is higher.
    """
    
    import os
    
    from glass.prop.ext           import get_extent
    from gesri.rd.shp       import shp_to_lyr
    from glass.to.shp.arcg        import geomArray_to_fc
    from glass.mob.arctbx.svarea  import service_area_polygon
    from glass.web.glg.distmatrix import get_max_dist
    
    if epsg != 4326:
        from glass.mng.prj import project
    
    arcpy.env.overwriteOutput = True
    
    # Get extent
    minX, maxX, minY, maxY = get_extent(extentLyr, gisApi='arcpy')
    
    # Get Reference points through the boundary
    # Get North West to East
    north_west_east = [(minX, maxY)]
    # Get South West to East
    south_west_east = [(minX, minY)]
    c = minX
    while c < maxX:
        north_west_east.append((c, maxY))
        south_west_east.append((c, minY))
        c += REF_DISTANCE
    
    north_west_east.append((maxX, maxY))
    south_west_east.append((maxX, minY))
    
    # Get West North to South
    west_north_to_south = [(minX, maxY)]
    # Get East North to South
    east_north_to_south = [(maxX, maxY)]
    c = maxY
    while c > minY:
        west_north_to_south.append((minX, c))
        east_north_to_south.append((maxX, c))
        c -= REF_DISTANCE
    
    west_north_to_south.append((minX, minY))
    east_north_to_south.append((maxX, minY))
    
    south_west_east.reverse()
    west_north_to_south.reverse()
    
    # Export Ref Points to a file only to see the result
    REF_GEOM = north_west_east + east_north_to_south + \
        south_west_east + west_north_to_south
    line_array = [{
        'FID': 0,
        "GEOM" : REF_GEOM
    }]
    
    REF_POINTS = os.path.join(os.path.dirname(output), 'extent.shp')
    geomArray_to_fc(line_array, REF_POINTS,
        "POLYLINE", epsg, overwrite=True
    )
    
    # Calculate time-distance between origins Lyr and reference points
    # Get Geom of originsLyr
    # Convert to WGS84
    if epsg != 4326:
        originsWGS = project(
            originsLyr, os.path.join(
                os.path.dirname(output), 'origins_wgs84.shp'
            ), 4326
        )
    else:
        originsWGS = originsLyr
    
    origLyr = shp_to_lyr(originsWGS)
    origPoint = []
    for line in arcpy.SearchCursor(origLyr):
        pnt = line.Shape.centroid
        
        origPoint.append((pnt.X, pnt.Y))
    
    # Get WGS REF POINTS
    if epsg != 4326:
        refWGS = project(
            REF_POINTS, os.path.join(
                os.path.dirname(output), 'extent_wgs.shp'
            ), 4326
        )
    else:
        refWGS = REF_POINTS
    
    refPointsLyr = shp_to_lyr(refWGS)
    refPoints = []
    for line in arcpy.SearchCursor(refPointsLyr):
        geom = line.getValue("Shape")
        
        for vector in geom:
            for pnt in vector:
                pnt_str = str(pnt).split(' ')
                refPoints.append((pnt_str[0], pnt_str[1]))
    
    # From that distances, get time intervals
    max_distance = get_max_dist(origPoint, refPoints)
    INTERVAL_RANGE = int(round(max_distance / NR_INTERVALS, 0))
    
    c = 0
    INTERVALS = []
    for i in range(NR_INTERVALS):
        INTERVALS.append(c + INTERVAL_RANGE)
        c += INTERVAL_RANGE
    
    # Run Service Area Tool
    service_area_polygon(networkDataset, rdvName, INTERVALS, originsLyr, output)
    
    return output


def service_area_as_sup_cst2(networkDataset, rdvName, extentLyr, originsLyr, output,
                            epsg, REF_DISTANCE=3000, NR_INTERVALS=20):
    """
    Create a Cost Distance Surface using Service Area Tool
    
    Same result of the Cost Distance tool but using Service Area Tool
    
    Support by ArcGIS Closest Facility tool
    """
    
    import os
    from glass.prop.ext           import get_extent
    from glass.cpu.arcg.mng.feat  import vertex_to_point
    from glass.cpu.arcg.mng.fld   import field_statistics
    from glass.cpu.arcg.geometry  import geomArray_to_polyline_gon
    from glass.mob.arctbx.closest import closest_facility
    from glass.mob.arctbx.svarea  import service_area_polygon
    
    arcpy.env.overwriteOutput = True
    
    # Get extent
    minX, maxX, minY, maxY = get_extent(extentLyr, gisApi='arcpy')
    
    # Get Reference points through the boundary
    # Get North West to East
    north_west_east = [(minX, maxY)]
    # Get South West to East
    south_west_east = [(minX, minY)]
    c = minX
    while c < maxX:
        north_west_east.append((c, maxY))
        south_west_east.append((c, minY))
        c += REF_DISTANCE
    
    north_west_east.append((maxX, maxY))
    south_west_east.append((maxX, minY))
    
    # Get West North to South
    west_north_to_south = [(minX, maxY)]
    # Get East North to South
    east_north_to_south = [(maxX, maxY)]
    c = maxY
    while c > minY:
        west_north_to_south.append((minX, c))
        east_north_to_south.append((maxX, c))
        c -= REF_DISTANCE
    
    west_north_to_south.append((minX, minY))
    east_north_to_south.append((maxX, minY))
    
    south_west_east.reverse()
    west_north_to_south.reverse()
    
    # Export Ref Points to a file only to see the result
    REF_GEOM = north_west_east + east_north_to_south + \
        south_west_east + west_north_to_south
    line_array = [{
        'FID': 0,
        "GEOM" : REF_GEOM
    }]
    
    REF_LINE = os.path.join(os.path.dirname(output), 'extent.shp')
    geomArray_to_polyline_gon(
        line_array,
        REF_LINE,
        "POLYLINE", epsg, overwrite=True
    )
    
    # Ref Line to Ref Points
    REF_POINTS = vertex_to_point(REF_LINE, os.path.join(
        os.path.dirname(output), 'extent_pnt.shp'
    ))
    
    REF_TABLE = os.path.join(
        os.path.dirname(output), 'time_ref_table.dbf'
    )
    closest_facility(
        networkDataset, rdvName, originsLyr, REF_POINTS,
        REF_TABLE, 
        oneway_restriction=True
    )
    
    # Get Maximum Time Registed
    MAX_DIST = field_statistics(REF_TABLE, 'Total_Minu', 'MAX')[0]
    
    INTERVAL_RANGE = int(round(MAX_DIST / NR_INTERVALS, 0))
    
    c = 0
    INTERVALS = []
    for i in range(NR_INTERVALS):
        INTERVALS.append(c + INTERVAL_RANGE)
        c += INTERVAL_RANGE
    
    # Run Service Area Tool
    service_area_polygon(
        networkDataset, rdvName, INTERVALS, originsLyr, output
    )
    
    return output

