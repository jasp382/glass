"""
Reclassify Raster files
"""

import os
import numpy as np
from osgeo import gdal

from glass.prop.img import get_nd, rst_epsg
from glass.wt.rst   import obj_to_rst


def rcls_rst(inrst, rclsRules, outrst, api='gdal', maintain_ext=True):
    """
    Reclassify a raster (categorical and floating points)
    
    if api == 'gdal
    rclsRules = {
        1 : 99,
        2 : 100
        ...
    }
    
    or
    
    rclsRules = {
        (0, 8) : 1
        (8, 16) : 2
        '*'     : 'NoData'
    }
    
    elif api == grass:
    rclsRules should be a path to a text file
    """
    
    if api == 'gdal':
        from glass.rd.rsrc import imgsrc_to_num

        if not os.path.exists(inrst):
            raise ValueError(f'File {inrst} does not exist!')

        # Open Raster
        img = gdal.Open(inrst)

        epsg = rst_epsg(img)
    
        # Raster to Array
        rst_num = imgsrc_to_num(img)
    
        nodataVal = get_nd(img)
    
        rcls_num = np.full(rst_num.shape, 255, dtype=np.uint8)
    
        # Change values
        for k in rclsRules:
            if rclsRules[k] == 'NoData': continue
            
            if type(k) == str: continue
            
            elif type(k) == tuple:
                q = (rst_num > k[0]) & (rst_num <= k[1])
            
            else:
                q = rst_num == k
            
            np.place(rcls_num, q, rclsRules[k])
    
        if '*' in rclsRules and rclsRules['*'] != 'NoData':
            np.place(rcls_num, rcls_num == 255, rclsRules['*'])
    
        if 'NoData' in rclsRules and rclsRules['NoData'] != 'NoData':
            np.place(rcls_num, rst_num == nodataVal, rclsRules['NoData'])
        
        if not maintain_ext:
            from glass.rst.rshp import rshp_to_data

            left, cellx, z, top, c, celly = img.GetGeoTransform()

            clip_rcls, n_left, n_top = rshp_to_data(rcls_num, 255, left, cellx, top, celly)

            gt = (n_left, cellx, z, n_top, c, celly)
            return obj_to_rst(clip_rcls, outrst, gt, epsg, noData=255)
        else:
            return obj_to_rst(
                rcls_num, outrst, img.GetGeoTransform(),
                epsg, noData=255
            )
    
    elif api == "grass":
        from glass.pys.oss import fprop
        from glass.pys.tm import now_as_str
        from glass.wenv.grs import run_grass
        from glass.rst.rcls.grs import rcls_rules

        ws, loc = os.path.dirname(outrst), f"loc_{now_as_str()}"

        gb = run_grass(ws, location=loc, srs=inrst)

        import grass.script.setup as gsetup
    
        gsetup.init(gb, ws, loc, 'PERMANENT')

        from glass.it.rst import rst_to_grs, grs_to_rst
        from glass.rst.rcls.grs import grs_rcls

        rules = rcls_rules(rclsRules, os.path.join(ws, loc, 'rclsrules.txt'))

        grsrst = rst_to_grs(inrst)
        rclsrst = grs_rcls(grsrst, rules, fprop(outrst, 'fn'), as_cmd=True)

        grs_to_rst(rclsrst, outrst, as_cmd=True, rtype=int)
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outrst


def rcls_rasters(rules):
    """
    Reclassify several rasters

    rules = [{
        "RASTER" : input,
        "RULES"  : reclassify rules,
        "OUT"    : output
    }, ...]
    """

    for i in rules:
        rcls_rst(i["RASTER"], i["RULES"], i["OUT"], api="grass")


"""
Other tools
"""

def rstval_to_binrst(rst, outfld, fileformat=None):
    """
    Export all values in a raster to new binary raster
    """
    
    from glass.pys.oss import fprop

    fileformat = fileformat if fileformat else '.tif'

    rst_src = gdal.Open(rst, gdal.GA_ReadOnly)

    # Get Nodata
    nd = rst_src.GetRasterBand(1).GetNoDataValue()

    # Data To Array
    rst_num = rst_src.GetRasterBand(1).ReadAsArray()

    # Get Unique values in Raster
    val = np.unique(rst_num)
    val = list(val[val != nd])

    fn = fprop(rst, 'fn')
    for v in val:
        # Create new binary array
        val_a = np.zeros(rst_num.shape, dtype=np.uint8)
        np.place(val_a, rst_num == v, 1)

        # Export to new raster
        _fn = f'{fn}_val{v}{fileformat}'
        obj_to_rst(
            val_a, os.path.join(outfld, _fn),
            rst_src.GetGeoTransform(),
            rst_epsg(rst_src), noData=0
        )
