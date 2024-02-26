"""
Local Tools
"""

import arcpy


def combine_rst(rsts, orst, ref):
    """
    Run Combine Rasters tool
    """

    from arcpy.sa import Combine
    
    arcpy.env.extent = ref
    arcpy.env.snapRaster = ref

    ocmb = Combine(rsts)

    ocmb.save(orst)

    arcpy.env.extent = None
    arcpy.env.snapRaster = None

    return orst, ocmb




def lookup(inrst, col, outrst, ref):
    """
    Lookup raster
    """

    from arcpy.sa import Lookup

    arcpy.env.extent = ref
    arcpy.env.snapRaster = ref

    orst = Lookup(inrst, col)

    orst.save(outrst)

    arcpy.env.extent = None
    arcpy.env.snapRaster = None

    return outrst, orst

