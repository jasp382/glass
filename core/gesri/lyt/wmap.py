"""
Methods to write maps
"""

import arcpy


def write_map(lytobj, outmap, dpi=None):
    """
    Export Layout to new file
    """

    from glass.pys.oss import fprop

    ff = fprop(outmap, 'ff')

    dpi = 500 if not dpi else dpi if type(dpi) == int else 500

    if ff == '.pdf':
        lytobj.exportToPDF(outmap, resolution=dpi)
    
    else:
        lytobj.exportToJPEG(outmap, resolution=dpi)
    
    return outmap

