"""
Network Analyst tools converted to Python
"""

import arcpy
import os


def closest_facility(nd, rdv, facilities, incidents, outtbl, oneway_name="",
    impedance_attr="TravelTime"):
    """
    Execute the Closest Facility tool - Produce Closest Facility Layer
    
    * facilities = destiny points
    * incidents = start/origins points
    """
    
    from glass.pys.oss     import fprop
    from glass.esri.rd.shp import shp_to_lyr
    from glass.esri.wt     import tbl_to_tbl
    
    """if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')"""
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = os.path.dirname(os.path.dirname(nd))
    
    oneway = oneway_name if type(oneway_name) == str else ""

    ndlyr = f"cf_{fprop(incidents, 'fn')}"

    junc = f"{os.path.basename(nd)}_Junctions"

    cfres = arcpy.na.MakeClosestFacilityLayer(
        in_network_dataset=nd,
        out_network_analysis_layer=ndlyr,
        impedance_attribute=impedance_attr,
        travel_from_to="TRAVEL_TO", 
        default_cutoff="",
        default_number_facilities_to_find="1",
        accumulate_attribute_name="",
        UTurn_policy="NO_UTURNS",
        restriction_attribute_name=oneway,
        hierarchy="NO_HIERARCHY",
        hierarchy_settings="",
        output_path_shape="TRUE_LINES_WITH_MEASURES",
        time_of_day="",
        time_of_day_usage="NOT_USED"
    )

    cflyr = cfres.getOutput(0)

    # Add Facilities
    flyr = shp_to_lyr(facilities, lyrname="cff")

    arcpy.na.AddLocations(
        in_network_analysis_layer=cflyr,
        sub_layer="Facilities",
        in_table=flyr,
        field_mappings="",
        search_tolerance="5000 Meters",
        sort_field="",
        search_criteria=f"{rdv} SHAPE;{junc} NONE",
        match_type="MATCH_TO_CLOSEST",
        append="APPEND",
        snap_to_position_along_network="NO_SNAP",
        snap_offset="5 Meters",
        exclude_restricted_elements="INCLUDE",
        search_query=f"{rdv} #;{junc} #"
    )
    
    # Add incidents
    ilyr = shp_to_lyr(incidents, lyrname='ilyr')

    arcpy.na.AddLocations(
        in_network_analysis_layer=cflyr,
        sub_layer="Incidents",
        in_table=ilyr,
        field_mappings="",
        search_tolerance="5000 Meters",
        sort_field="",
        search_criteria=f"{rdv} SHAPE;{junc} NONE",
        match_type="MATCH_TO_CLOSEST",
        append="APPEND",
        snap_to_position_along_network="NO_SNAP",
        snap_offset="5 Meters",
        exclude_restricted_elements="INCLUDE",
        search_query=f"{rdv} #;{junc} #"
    )
    
    # Solve
    arcpy.na.Solve(
        in_network_analysis_layer=cflyr,
        ignore_invalids="SKIP",
        terminate_on_solve_error="TERMINATE",
        simplification_tolerance="",
        overrides=""
    )
    
    tbl_to_tbl(f"{ndlyr}\\Routes", outtbl)

    return outtbl

