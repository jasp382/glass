
import arcpy

def composite_bands(bands, orst):

    bstr = ";".join(bands)

    arcpy.CompositeBands_management(bstr, orst)

    return orst

