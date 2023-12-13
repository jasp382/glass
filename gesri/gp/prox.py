"""
ArcGIS Proximity Tools
"""

import arcpy


def geom_to_buffer(geometry, buf_distance):
    """
    Receive a Geometry object and create a buffer
    """
    
    geometry = geometry if type(geometry) == list else [geometry]
    
    for g in range(len(geometry)):
        geometry[g] = geometry[g].buffer(buf_distance)
    
    return geometry[0] if len(geometry) == 1 else geometry


def dist_bet_same_points_different_featcls(pntA, pntB, attrA, attrB,
                                           distField='distance'):
    """
    Calculate distance between the same points in different feature classes.
    
    The script knows that the point is the same in pntA and pntB if the
    value of attrA is equal to the value of attrB
    """
    
    from gesri.rd.shp   import shp_to_lyr
    from gesri.tbl.cols import add_col
    
    arcpy.env.overwriteOutput = True
    
    # List features in pntA
    lyrA = shp_to_lyr(pntA)
    cursor = arcpy.SearchCursor(lyrA)
    line = cursor.next()
    
    dA = {}
    while line:
        attr = line.getValue(attrA)
        geom = line.Shape.centroid
        
        if attr not in dA:
            dA[attr] = (geom.X, geom.Y)
        
        else:
            raise ValueError(
                'AttrA and AttrB can not have duplicated values'
            )
        
        line = cursor.next()
    
    del cursor
    del line
    
    # Calculate distance between points
    add_col(
        lyrA, distField, "DOUBLE", "6", precision="4"
    )
    
    lyrB = shp_to_lyr(pntB)
    cursor = arcpy.SearchCursor(lyrB)
    line = cursor.next()
    
    dist = {}
    while line:
        attr = line.getValue(attrB)
        
        if attr in dA.keys():
            xa, ya = dA[attr]
            
            geom = line.Shape.centroid
            
            xb, yb = (geom.X, geom.Y)
            
            dist[attr] = ((xb - xa)**2 + (yb - ya)**2)**0.5
        
        line = cursor.next()
    
    del cursor
    del line
    
    cursor = arcpy.UpdateCursor(lyrA)
    for line in cursor:
        attr = line.getValue(attrA)
        
        if attr in dist:
            line.setValue(distField, dist[attr])
            
            cursor.updateRow(line)


def find_point_in_line_by_point(inPoint, inLine):
    """
    Finds the point on the polyline nearest to the in_point and
    the distance between those points.
    Also returns information about the side of the line the
    in_point is on as well as the distance along the line
    where the nearest point occurs.
    """
    
    return inLine.queryPointAndDistance(inPoint)


def distance_to(geom_1, geom_2):
    """
    Returns the minimum distance between two geometries
    """
    
    return geom_1.distanceTo(geom_2)


def near_anls(inShp, distToShp, searchRadius=None, joinData=None):
    """
    Find near Features in other Feature Class
    """
    
    arcpy.Near_analysis(
        inShp, distToShp, "" if not searchRadius else searchRadius,
        "NO_LOCATION" if not joinData else "LOCATION",
        "NO_ANGLE", "PLANAR"
    )
    
    return inShp
