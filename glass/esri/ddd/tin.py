"""
TIN Operations
"""

import arcpy


def create_tin(outTin, prj, inputStr):
    """
    Execute Create TIN from 3D Analyst Tools
    """
    
    arcpy.ddd.CreateTin(outTin, prj, inputStr, "DELAUNAY")


def countours_to_tin(elevation, elvfield, lmt, prj, output, hydrology=None):
    """
    Create Raster DEM from TIN
    """
    
    from glass.pys.oss    import fprop
    from glass.pys.tm import now_as_str
    from glass.esri.rd.shp import shp_to_lyr

    nstr = now_as_str(utc=True)
    
    lyr_elev  = shp_to_lyr(elevation, lyrname=f'elv_{nstr}')
    lyr_lmt   = shp_to_lyr(lmt, lyrname=f'sclip_{nstr}')
    lyr_hidro = shp_to_lyr(hydrology, lyrname=f'hyd_{nstr}') \
        if hydrology else None
    
    hydrostr = '' if not hydrology else \
        f"; {lyr_hidro[0].shape} <None> Hard_Line <None>"
    
    __inputs = (
        f"{lyr_lmt[0].name} <None> Soft_Clip <None>; "
        f"{lyr_elev[0].name} {elvfield} Mass_Points <None>"
        f"{hydrostr}"
    )
    
    create_tin(output, prj, __inputs)
    
    return output
