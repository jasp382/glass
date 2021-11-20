import arcpy


"""
Deal with conversion between Geometric Primitives
"""

def feat_to_pnt(shp, o, pnt_position="CENTROID"):
    """
    pnt_position = "CENTROID" ? "INSIDE"
    """
    
    arcpy.FeatureToPoint_management(shp, o, pnt_position)
    
    return o


def vertex_to_point(shp, o):
    
    arcpy.FeatureVerticesToPoints_management(
        in_features=shp, 
        out_feature_class=o, 
        point_location="ALL"
    )
    
    return o

def polygons_from_points(inputPnt, outputPol, prj, POLYGON_FIELD,
                         ORDER_FIELD=None):    
    """
    Create a Polygon Table from a Point Table
    
    A given Point Table:
    FID | POLYGON_ID | ORDER_FIELD
     0  |    P1      |      1
     1  |    P1      |      2
     2  |    P1      |      3
     3  |    P1      |      4
     4  |    P2      |      1
     5  |    P2      |      2
     6  |    P2      |      3
     7  |    P2      |      4
     
    Will be converted into a new Polygon Table:
    FID | POLYGON_ID
     0  |    P1
     1  |    P2
     
    In the Point Table, the POLYGON_ID field identifies the Polygon of that point,
    the ORDER FIELD specifies the position (first point, second point, etc.)
    of the point in the polygon.
    
    If no ORDER field is specified, the points will be assigned to polygons
    by reading order.
    """
    
    import os
    from glass.cpu.arcg.lyr         import feat_lyr
    from glass.cpu.arcg.mng.featcls import create_feat_class
    from glass.cpu.arcg.mng.fld     import add_field
    from glass.cpu.arcg.mng.fld     import type_fields
    
    arcpy.env.overwriteOutput = True
    
    # TODO: Check Geometry of the Inputs
    
    # List all point
    pntLyr = feat_lyr(inputPnt)
    cursor = arcpy.SearchCursor(pntLyr)
    line   = cursor.next()
    
    lPnt = {}
    cnt = 0
    while line:
        # Get Point Geom
        pnt = line.Shape.centroid
        # Get Polygon Identification
        polygon = line.getValue(POLYGON_FIELD)
        # Get position in the polygon
        order = line.getValue(ORDER_FIELD) if ORDER_FIELD else cnt
        
        # Store data
        if polygon not in lPnt.keys():
            lPnt[polygon] = {order : (pnt.X, pnt.Y)}
        
        else:
            lPnt[polygon].update({order : (pnt.X, pnt.Y)})
        
        line = cursor.next()
        cnt += 1
    
    del line
    del cursor
    
    # Write Output
    create_feat_class(
        outputPol, "POLYGON", prj
    )
    
    outLyr = feat_lyr(outputPol)
    
    # Add polygon ID
    fieldsPnt = type_fields(pntLyr)
    
    POLYGON_FIELD_TYPE = "TEXT" if fieldsPnt[POLYGON_FIELD] == 'String' \
        else "SHORT" if fieldsPnt[POLYGON_FIELD] == 'Integer' else \
        "TEXT"
    POLYGON_FIELD_PRECISION = 50 if POLYGON_FIELD_TYPE == "TEXT" else \
        15
    
    add_field(
        outLyr, POLYGON_FIELD,
        POLYGON_FIELD_TYPE,
        POLYGON_FIELD_PRECISION
    )   
    
    cursor = arcpy.InsertCursor(outLyr)
    
    # Add Polygons
    point = arcpy.CreateObject("Point")
    for polygon in lPnt:
        vector = arcpy.CreateObject("Array")
        
        pnt_order = lPnt[polygon].keys()
        pnt_order.sort()
        
        for p in pnt_order:
            point.ID = p
            point.X = lPnt[polygon][p][0]
            point.Y = lPnt[polygon][p][1]
            vector.add(point)
        
        # Add last point
        point.X = lPnt[polygon][pnt_order[0]][0]
        point.Y = lPnt[polygon][pnt_order[0]][1]
        vector.add(point)
        
        new_row = cursor.newRow()
        new_row.Shape = vector
        
        new_row.setValue(POLYGON_FIELD, str(polygon))
        
        cursor.insertRow(new_row)
        
        vector = 0

