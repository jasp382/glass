"""
Resample stuff
"""

import os
import arcpy


def warp_rst(rst, outrst, srcpnt, tgpnt, rst_format='.tif'):
    """
    Warp Raster

    srcpnt example:
    srcpnt = (
        "'16.2409649994254 48.0598321302268';'16.3212880027982 48.1005354388663';"
        "'16.2409649994254 48.1005354388663';'16.3212880027982 48.0598321302268'"
    )

    tgpnt = (
        "'16.240965 48.0633562';'16.3212877 48.0963069';"
        "'16.240965 48.0963069';'16.3212877 48.0633562'"
    )
    """

    rst_format = '.tif' if not rst_format else rst_format

    if os.path.isdir(rst):
        from glass.pys.oss import lst_ff

        rsts = lst_ff(rst, file_format=rst_format)
    
    else:
        from glass.pys import obj_to_lst

        rsts = obj_to_lst(rst)
    
    if os.path.isdir(outrst):
        outrsts = [os.path.join(
            outrst, 'warp_{}'.format(os.path.basename(r))
        ) for r in rsts]
    
    else:
        if type(outrst) != list:
            if len(rsts) > 1:
                outrsts = [os.path.join(
                    os.path.dirname(outrst), 'warp_{}'.format(os.path.basename(r))
                ) for r in rsts]
            
            else:
                outrsts = [outrst]
        
        else:
            outrsts = outrst
    
    for r in range(len(rsts)):
        arcpy.Warp_management(
            rsts[r], srcpnt, tgpnt, outrsts[r], "POLYORDER1", "BILINEAR"
        )

    return outrst
