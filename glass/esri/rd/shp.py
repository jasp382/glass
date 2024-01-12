"""
Read files
"""


import arcpy


def shp_to_lyr(shp, lyrname=None):
    """
    Feature class to layer
    """

    from glass.pys.oss import fprop

    n = fprop(shp, 'fn') if not lyrname or \
        type(lyrname) != str else lyrname

    lyr = arcpy.MakeFeatureLayer_management(shp, n)

    return lyr
