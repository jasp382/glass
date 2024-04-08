"""
Network Analyst tools converted to Python
"""

import arcpy
import os


def closest_facility(nd, facilities, incidents, outtbl, oneway_name="",
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

    # Get Sources
    _nd = arcpy.nax.NetworkDataset(nd)
    desc = _nd.describe()

    ndsrc = []
    for src in desc.edgeSources:
        ndsrc.append(src.name)
    
    # Get Junctions
    jsrc = []
    for j in desc.junctionSources:
        jsrc.append(j.name)
    
    # Search criteria string
    search_criteria1 = ";".join([f"{x} SHAPE" for x in ndsrc])
    search_criteria2 = ";".join([f"{y} NONE" for y in jsrc])
    scriteria = f"{search_criteria1};{search_criteria2}"

    # Search query string
    search_q = ";".join([f"{z} #" for z in ndsrc + jsrc])

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
        search_criteria=scriteria,
        match_type="MATCH_TO_CLOSEST",
        append="APPEND",
        snap_to_position_along_network="NO_SNAP",
        snap_offset="5 Meters",
        exclude_restricted_elements="INCLUDE",
        search_query=search_q
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
        search_criteria=scriteria,
        match_type="MATCH_TO_CLOSEST",
        append="APPEND",
        snap_to_position_along_network="NO_SNAP",
        snap_offset="5 Meters",
        exclude_restricted_elements="INCLUDE",
        search_query=search_q
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


def service_area(nd, tmint, facilities, outshp, overlap="overlap", 
                 impedance="DriveTime", to_facility=True, detailed=True):
    """
    Execute Service Area tool - Produce Service Area Layer

    overlap options:
    * overlap
    * split
    * dissolve
    """

    arcpy.env.overwriteOutput = True

    ndOverlap = arcpy.nax.ServiceAreaOverlapGeometry.Split if \
        overlap == "split" else arcpy.nax.ServiceAreaOverlapGeometry.Dissolve \
        if overlap == "dissolve" else arcpy.nax.ServiceAreaOverlapGeometry.Overlap
    tofrom_fac = arcpy.nax.TravelDirection.ToFacility if to_facility else \
        arcpy.nax.TravelDirection.FromFacility
    
    poly_detail = arcpy.nax.ServiceAreaPolygonDetail.High if detailed \
        else arcpy.nax.ServiceAreaPolygonDetail.Standard

    nd_lyr = os.path.basename(nd)

    arcpy.nax.MakeNetworkDatasetLayer(nd, nd_lyr)

    # Get Travel Mode
    tvmodes = arcpy.nax.GetTravelModes(nd_lyr)
    tvmod   = tvmodes[impedance] if impedance else \
        tvmodes(tvmodes.keys()[0])
    
    # Instantiate a ServiceArea solver object
    sasrv = arcpy.nax.ServiceArea(nd_lyr)

    # Set properties
    sasrv.timeUnits         = arcpy.nax.TimeUnits.Minutes
    sasrv.defaultImpedanceCutoffs = tmint
    sasrv.travelMode        = tvmod
    sasrv.outputType        = arcpy.nax.ServiceAreaOutputType.Polygons
    sasrv.geometryAtOverlap = ndOverlap
    sasrv.travelDirection   = tofrom_fac
    sasrv.polygonDetail     = poly_detail

    # Load inputs
    sasrv.load(arcpy.nax.ServiceAreaInputDataType.Facilities, facilities)
    # Solve the analysis
    result = sasrv.solve()

    # Export the results to a feature class
    if result.solveSucceeded:
        result.export(arcpy.nax.ServiceAreaOutputDataType.Polygons, outshp)
    else:
        print("Solve failed")
        print(result.solverMessages(arcpy.nax.MessageSeverity.All))

        result = None

    return result

