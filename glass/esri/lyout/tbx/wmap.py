"""
Write Maps with ArcPY
"""

import arcpy


def mxd_saveas(mxdObj, outMxd):
    """
    Save a copy of a MXD file
    """
    
    mxdObj.saveACopy(outMxd)
    
    return outMxd


def write_map(mxd_obj, outMap, dpi=None):
    """
    Export mxd obj to a new file
    """
    
    import os
    from glass.pys.oss import get_fileformat
    
    dpi = 300 if not dpi else dpi if type(dpi) == int else 300
    
    mapFileFormat = get_fileformat(outMap)
    
    if mapFileFormat == '.jpg':
        arcpy.mapping.ExportToJPEG(
            mxd_obj, outMap, resolution=dpi
        )
    
    elif mapFileFormat == '.pdf':
        arcpy.mapping.ExportToPDF(
            mxd_obj, outMap, resolution=dpi
        )
    
    elif mapFileFormat == '.png':
        arcpy.mapping.ExportToPNG(
            mxd_obj, outMap, resolution=dpi
        )
    
    elif mapFileFormat == '.gif':
        arcpy.mapping.ExportToGIF(
            mxd_obj, outMap, resolution=dpi
        )
    
    elif mapFileFormat == '.tiff' or mapFileFormat == '.tif':
        arcpy.mapping.ExportToTIFF(
            mxd_obj, outMap, resolution=dpi
        )
    
    elif mapFileFormat == '.eps':
        arcpy.mapping.ExportToEPS(
            mxd_obj, outMap, resolution=dpi
        )
    
    else:
        raise ValueError('File format of output map is not valid')
    
    return outMap


def write_maps_forFolderMXDs(folder, map_format='.jpg'):
    """
    Export map for all mxd in one folder
    """
    
    import os
    from glass.pys.oss import lst_ff, get_filename
    
    mxds = lst_ff(folder, file_format='.mxd')
    
    for mxd in mxds:
        __mxd = arcpy.mapping.MapDocument(mxd)
        
        write_map(__mxd, os.path.join(
            folder, get_filename(mxd) + map_format
        ))

