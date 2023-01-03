"""
Reclassify Raster files
"""

import os

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
        import numpy          as np
        import os
        from osgeo            import gdal
        from glass.wt.rst   import obj_to_rst
        from glass.rd.rsrc  import imgsrc_to_num
        from glass.prop.img import get_nd

        if not os.path.exists(inrst):
            raise ValueError('File {} does not exist!'.format(inrst))

        # Open Raster
        img = gdal.Open(inrst)
    
        # Raster to Array
        rst_num = imgsrc_to_num(img)
    
        nodataVal = get_nd(img)
    
        rcls_num = np.full(rst_num.shape, 255, dtype=np.uint8)
    
        # Change values
        for k in rclsRules:
            if rclsRules[k] == 'NoData':
                continue
            
            if type(k) == str:
                continue
            
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

            return obj_to_rst(clip_rcls, outrst, img, noData=255, geotrans=(
                n_left, cellx, z, n_top, c, celly
            ))
        else:
            return obj_to_rst(rcls_num, outrst, img, noData=255)
    
    elif api == "pygrass":
        from grass.pygrass.modules import Module
        
        r = Module(
            'r.reclass', input=inrst, output=outrst, rules=rclsRules,
            overwrite=True, run_=False, quiet=True
        )
        
        r()
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outrst


"""
Reclassify in GRASS GIS
"""


def interval_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, intervals will be 
    converted in new values
    
    dic = {
        [lower_class_value, upper_class_value] : new_value1,
        (lower_class_value, upper_class_value) : new_value2,
        ...,
        (lower_class_value, upper_class_value) : new_valuen
    }
    """
    
    import os
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for nv in dic:
            thru = [
                f'{str(nv[i-1])} thru {str(nv[i])}'
            for i in range(1, len(nv), 2)]

            txt.write(f'{"  ".join(thru)}  = {str(dic[nv])}\n')
        
        txt.close()
    
    return out_rules


def category_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, categorical values will be
    converted into new designations/values
    
    dic = {
        old_value : new_value,
        old_value : new_value,
        ...
    }
    """
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for k in dic:
            txt.write(
                '{n}  = {o}\n'.format(o=str(dic[k]), n=str(k))
            )
        
        txt.close()
    
    return out_rules


def set_null(rst, value, ascmd=None):
    """
    Null in Raster to Some value
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.null', map=rst, setnull=value, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd("r.null map={} setnull={} --quiet".format(
            rst, value
        ))


def null_to_value(rst, value, as_cmd=None):
    """
    Give a numeric value to the NULL cells
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.null', map=rst, null=value, run_=False, quiet=True
        )
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd(f"r.null map={rst} null={value} --quiet")


"""
Other tools
"""

def rstval_to_binrst(rst, outfld, fileformat=None):
    """
    Export all values in a raster to new binary raster
    """

    import os
    import numpy as np
    from osgeo import gdal
    from glass.wt.rst import obj_to_rst
    from glass.pys.oss  import fprop

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
        obj_to_rst(val_a, os.path.join(
            outfld, fn + '_val' + str(v) + fileformat
        ), rst_src, noData=0)
