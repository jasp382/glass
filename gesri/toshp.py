"""
Something to Feature Class using ArcGIS tools
"""

import arcpy

"""
Array to Feature Class
"""
def geomArray_to_fc(array, output, GEOM_TYPE, EPSG, overwrite=True, fields=None):
    """
    Convert a array as
    array = [
        {
            "FID" : 0,
            "OTHER_FIELDS" : value
            "GEOM" : [(x1, y1), ..., (xn, yn)]
        },
        ...,
        {
            "FID" : 1,
            "OTHER_FIELDS" : value
            "GEOM" : [(x1, y1), ..., (xn, yn)]
        },
    ]
    
    to a new Feature Class
    
    If fields, it should have a value like:
    {name : [type, length], name: [type, length]}
    """
    
    from glass.cpu.arcg.mng.featcls import create_feat_class
    from gesri.rd.shp         import shp_to_lyr
    from gesri.tbl.cols     import add_col
    
    if overwrite: arcpy.env.overwriteOutput = True
    
    # Create a new Feature Class
    output = create_feat_class(output, GEOM_TYPE, EPSG)
    
    outLyr = shp_to_lyr(output)
    
    # Create fields
    if fields:
        if type(fields) != dict:
            raise ValueError(
                'FIELDS should be a dict'
            )
        
        else:
            for fld in fields:
                add_col(
                    outLyr, fld, fields[fld][0],
                    fields[fld][1]
                )
    
    # Add things to the feature class
    cursor = arcpy.InsertCursor(outLyr)
    point = arcpy.CreateObject("Point")
    for line in array:
        vector = arcpy.CreateObject("Array")
        
        c = 0
        for pnt in line["GEOM"]:
            point.ID = c
            point.X = pnt[0]
            point.Y = pnt[1]
            vector.add(point)
            c += 1
        
        new_row = cursor.newRow()
        new_row.Shape = vector
        
        # Add field values
        if fields:
            for fld in fields:
                if fld in line:
                    new_row.setValue(fld, line[fld])
        
        cursor.insertRow(new_row)
        
        vector = 0
    
    return output


"""
Files to Feature Class
"""

def kml_to_geodatabase(inKml, outLocation, nameGeoDb):
    """
    KML to GeoDatabase
    """
    
    arcpy.KMLToLayer_conversion(inKml, outLocation,nameGeoDb)


def osm_to_featurecls(osmXml, outGeoDatabase):
    """
    OSM XML File to Feature Classes
    """
    
    import os
    from glass.pys.oss             import get_filename
    from glass.cpu.arcg.mng.wspace import create_geodb
    
    PATH_TO_OSMTBX = r'C:\Program Files (x86)\ArcGIS\Desktop10.5\ArcToolbox\Toolboxes\OpenStreetMap Toolbox.tbx'
    
    arcpy.ImportToolbox(PATH_TO_OSMTBX)
    
    geodb = create_geodb(
        os.path.dirname(outGeoDatabase), get_filename(outGeoDatabase)
    )
    
    base_name = get_filename(osmXml)
    featDataset = os.path.join(outGeoDatabase, base_name)
    
    arcpy.OSMGPFileLoader_osmtools(
        osmXml, "CONSERVE_MEMORY", "ALL",
        featDataset, os.path.join(featDataset, 'osm_pnts'),
        os.path.join(featDataset, 'osm_lnhs'),
        os.path.join(featDataset, 'osm_poly')
    )
    
    return outGeoDatabase, base_name, {
        "POINTS"   : base_name + '_osm_pt',
        "LINES"    : base_name + '_osm_ln',
        "POLYGONS" : base_name + 'osm_ply'
    }


def txt_to_pnt(inTxt, pntShp, srs):
    """
    Text file to Point Feature Class
    """
    
    from glass.web.srorg        import get_wkt_esri
    from glass.arcg.mng.featcls import create_feat_class
    
    # Create new feature class
    create_feat_class(
        pntShp, "POINT", get_wkt_esri(srs)
    )
    
    with open(inTxt, mode='r') as txt:
        cursor = arcpy.InsertCursor(pntShp)
        
        lines = txt.readlines()
        
        for line in lines:
            pnt = arcpy.CreateObject("Point")
            
            vals = line.split(" ")
            
            pnt.ID, pnt.X, pnt.Y = vals
            
            new_row = cursor.newRow()
            new_row.Shape = pnt
            cursor.insertRow(new_row)
        
        txt.close()
    
    return pntShp


"""
From Raster to Feature Class
"""
def rst_to_pnt(inRst, pntShp, rstField=None):
    """Raster to Points Feature Class"""
    
    rstField = 'Value' if not rstField else rstField
    
    arcpy.RasterToPoint_conversion(
        in_raster=inRst, out_point_features=pntShp,
        raster_field=rstField
    )
    
    return pntShp


def rst_to_polyg(inRst, outShp, rstColumn=None):
    """
    Raster to Polygon Shapefile
    """
    
    rstField = 'Value' if not rstColumn else rstColumn
        
    import arcpy
        
    arcpy.RasterToPolygon_conversion(
        in_raster=inRst, out_polygon_features=outShp, 
        simplify=None, 
        raster_field=rstField
    )
    
    return outShp


def rasterFolder_to_points(rstFolder, pntFolder, rst_field=None,
                           outShpFormat='.shp'):
    """
    Raster to Points Feature Class
    """
    
    import os
    
    arcpy.env.workspace = rstFolder
    
    lst_rst = arcpy.ListRasters()
    
    outShpFormat = outShpFormat if outShpFormat[0] == '.' else \
        '.' + outShpFormat
    
    for rst in lst_rst:
        rst_to_point(
            rst, os.path.join(
                pntFld,
                os.path.splitext(os.path.basename(rst))[0] + outShpFormat
            ), rstField=rst_field
        )


"""
Geodatabase to Single File
"""

def gdb_to_shp(workspace, outworkspace):
    """
    Export all feature classes in a Geodatabase to a single file.
    Do this for all Geodatabases in workspace.
    """
    
    import os
    from gesri.dp import copy_feat
    
    # List GeoDatabases
    lst_gdb = arcpy.ListWorkspaces(workspace_type="FileGDB")
    
    dic_gdb = {}
    
    for gdb in lst_gdb:
        arcpy.env.workspace = gdb
        
        dic_gdb[gdb] = {}
        
        dts = arcpy.ListDatasets()
        
        for dt in dts:
            dic_gdb[gdb][dt] = arcpy.ListFeatureClasses(feature_dataset=dt)
    
    for gdb in dic_gdb:
        for dt in dic_gdb[gdb]:
            for fc in dic_gdb[gdb][dt]:
                copy_feat(
                    os.path.join(gdb, dt, fc),
                    os.path.join(outworkspace, "{}_{}.shp".format(
                        os.path.splitext(os.path.basename(gdb))[0],
                        fc
                    )), gisApi='arcpy'
                )

