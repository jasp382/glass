"""
ArcToolbox > Data Management Tools > Workspace
"""

import arcpy
import os

def create_geodb(workspace, name):
    """
    Create File Geodatabase
    """
    
    geoname = name if '.gdb' in name else name + '.gdb'
    
    arcpy.CreateFileGDB_management(workspace, geoname)
    
    return os.path.join(workspace, geoname)


def create_featdts(geodb, name, epsg_code):
    """
    Create Feature Dataset in existing GeoDataBase
    """
    
    
    from glass.web.srorg import get_wkt_esri
    
    arcpy.CreateFeatureDataset_management(
        geodb, name,
        get_wkt_esri(epsg_code) if epsg_code != 3857 else os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'epsg_3857.prj'
        )
    )
    
    return os.path.join(geodb, name)

