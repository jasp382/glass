"""
Network Analyst tools converted to Python

Service Area Utilizations
"""

import arcpy
import os


def get_sa(net, rdv, time_interval, loc, out,
            ONEWAY_RESTRICTION=True, OVERLAP=True):
    """
    Execute service area tool
    """
    
    from glass.esri.dp import copy_feat
    
    if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
        
    else:
        raise ValueError('Network analyst extension is not avaiable')
    
    network_name = str(os.path.basename(net))
    JUNCTIONS    = network_name + '_Junctions'
    
    oneway = "" if not ONEWAY_RESTRICTION else "Oneway"
    
    INTERVALS = str(time_interval) if type(time_interval) == int or \
        type(time_interval) == float else time_interval if \
        type(time_interval) == str \
        else ' '.join([str(int(x)) for x in time_interval]) if \
        type(time_interval) == list else None
    
    if not INTERVALS: raise ValueError((
        'time_interval format is not valid'
    ))
    
    arcpy.MakeServiceAreaLayer_na(
        in_network_dataset=net, 
        out_network_analysis_layer="servArea", 
        impedance_attribute="Minutes", 
        travel_from_to="TRAVEL_FROM", 
        default_break_values=INTERVALS, 
        polygon_type="DETAILED_POLYS", 
        merge="NO_MERGE" if OVERLAP else "NO_OVERLAP", 
        nesting_type="RINGS", 
        line_type="NO_LINES", 
        overlap="OVERLAP" if OVERLAP else "NON_OVERLAP", 
        split="NO_SPLIT", 
        excluded_source_name="", 
        accumulate_attribute_name="", 
        UTurn_policy="NO_UTURNS", 
        restriction_attribute_name=oneway, 
        polygon_trim="NO_TRIM_POLYS", 
        poly_trim_value="100 Meters", 
        lines_source_fields="NO_LINES_SOURCE_FIELDS", 
        hierarchy="NO_HIERARCHY", 
        time_of_day=""
    )
    
    # Add locations to the service area layer
    arcpy.AddLocations_na(
        "servArea", "Facilities", loc, "", "5000 Meters", "",
        "{_rdv} SHAPE;{j} NONE".format(_rdv=str(rdv), j=str(JUNCTIONS)),
        "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
        "{_rdv} #;{j} #".format(_rdv=str(rdv), j=str(JUNCTIONS))
    )
    # Solve
    arcpy.Solve_na("servArea", "SKIP", "TERMINATE", "")
    # Export to a shapefile
    save_servArea = copy_feat("servArea\\Polygons", out, gisApi='arcpy')
    
    return save_servArea


def service_area_use_meters(net, rdv, distance, loc, out,
                         OVERLAP=True, ONEWAY=None):
    """
    Execute service area tool using metric distances
    """
    
    from gesri.dp import copy_feat
    
    if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
        
    else:
        raise ValueError('Network analyst extension is not avaiable')
    
    network_name = str(os.path.basename(net))
    JUNCTIONS = network_name + '_Junctions'
    
    oneway = "" if not ONEWAY else "Oneway"
    
    INTERVALS = str(distance) if type(distance) == int or \
        type(distance) == float else distance if \
        type(distance) == str \
        else ' '.join([str(int(x)) for x in distance]) if \
        type(distance) == list else None
    
    if not INTERVALS: raise ValueError((
        'distance format is not valid'
    ))
    
    arcpy.MakeServiceAreaLayer_na(
        in_network_dataset=net, 
        out_network_analysis_layer="servArea", 
        impedance_attribute="Length", 
        travel_from_to="TRAVEL_FROM", 
        default_break_values=INTERVALS, 
        polygon_type="DETAILED_POLYS", 
        merge="NO_MERGE" if OVERLAP else "NO_OVERLAP", 
        nesting_type="RINGS", 
        line_type="NO_LINES", 
        overlap="OVERLAP" if OVERLAP else "NON_OVERLAP", 
        split="NO_SPLIT", 
        excluded_source_name="", 
        accumulate_attribute_name="", 
        UTurn_policy="NO_UTURNS", 
        restriction_attribute_name=oneway, 
        polygon_trim="TRIM_POLYS", 
        poly_trim_value="250 Meters", 
        lines_source_fields="NO_LINES_SOURCE_FIELDS", 
        hierarchy="NO_HIERARCHY", 
        time_of_day=""
    )
    
    # Add locations to the service area layer
    arcpy.AddLocations_na(
        "servArea", "Facilities", loc, "", "5000 Meters", "",
        "{_rdv} SHAPE;{j} NONE".format(_rdv=str(rdv), j=str(JUNCTIONS)),
        "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
        "{_rdv} #;{j} #".format(_rdv=str(rdv), j=str(JUNCTIONS))
    )
    # Solve
    arcpy.Solve_na("servArea", "SKIP", "TERMINATE", "")
    # Export to a shapefile
    save_servArea = copy_feat("servArea\\Polygons", out, gisApi='arcpy')
    
    return save_servArea

