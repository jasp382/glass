"""
Network Analyst tools converted to Python
"""

import arcpy
import os


def closest_facility(network, rdv_name, facilities, incidents, table,
                    oneway_restriction=False):
    """
    Execute the Closest Facility tool - Produce Closest Facility Layer
    
    * facilities = destiny points
    * incidents = start/origins points
    """
    
    from glass.pys.oss import fprop
    from gesri.dct.fmshp import shp_to_lyr
    from gesri.dct.toshp import tbl_to_tbl
    
    """if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')"""
    
    if oneway_restriction:
        oneway = "Oneway"
    else:
        oneway = ""
    
    nName = str(os.path.basename(network))
    junc = nName + '_Junctions'

    cf_lyr = "cf_{}".format(fprop(incidents, 'fn'))
    
    arcpy.MakeClosestFacilityLayer_na(
        in_network_dataset=network, 
        out_network_analysis_layer=cf_lyr, 
        impedance_attribute="Minutes",
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
    
    lyr_fa = shp_to_lyr(facilities)
    arcpy.AddLocations_na(
        cf_lyr, "Facilities", lyr_fa, "", "5000 Meters", "",
        "{_rdv} SHAPE;{j} NONE".format(_rdv=str(rdv_name), j=str(junc)),
        "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
        "{_rdv} #;{j} #".format(_rdv=str(rdv_name), j=str(junc))
    )
    
    lyr_in = shp_to_lyr(incidents)
    arcpy.AddLocations_na(
        cf_lyr, "Incidents", lyr_in, "", "5000 Meters", "",
        "{_rdv} SHAPE;{j} NONE".format(_rdv=str(rdv_name), j=str(junc)),
        "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
        "{_rdv} #;{j} #".format(_rdv=str(rdv_name), j=str(junc))
    )
    
    arcpy.Solve_na(cf_lyr, "SKIP", "TERMINATE", "")
    
    tbl_to_tbl(cf_lyr + "\\Routes", table)

    return table

