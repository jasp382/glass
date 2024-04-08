"""
Raster Data Type Transformation
"""

import os
import numpy as np
from osgeo import gdal

from glass.wt.rst   import obj_to_rst
from glass.prop.img import rst_epsg


def conv_rst_dtype(rst, out, odtype, place_nodata=None, newndval=None):
    """
    Change Raster Dtype

    odtype options:
    * byte
    * int8
    * uint8
    * int16
    * uint16
    * int32
    * uint32
    * float32
    """
    
    # Open Raster
    src = gdal.Open(rst, gdal.GA_ReadOnly)
    imgnum = src.ReadAsArray()

    # Get geotrans
    gtrans = src.GetGeoTransform()

    # Get EPSG
    epsg = rst_epsg(src)

    # Get nodata value
    ndval = src.GetRasterBand(1).GetNoDataValue()

    # Get new data type
    if odtype == 'int8':
        dt = np.int8
        ndval = int(ndval)

    elif odtype == 'uint8':
        dt = np.uint8
        ndval = int(ndval)

    elif odtype == 'int16':
        dt = np.int16
        ndval = int(ndval)

    elif odtype == 'uint16':
        dt = np.uint16
        ndval = int(ndval)

    elif odtype == 'int32':
        dt = np.int32
        ndval = int(ndval)

    elif odtype == 'uint32':
        dt = np.uint32
        ndval = int(ndval)
    
    elif odtype == 'float32':
        dt = np.float32
        ndval = float(ndval)
    
    elif odtype == 'byte':
        dt = np.byte
        ndval = int(ndval)
    
    else:
        dt = np.float32
        ndval = float(ndval)

    # Data type conversion
    newnum = imgnum.astype(dt)

    if place_nodata and newndval:
        if place_nodata[0] == '<':
            exp = newnum < place_nodata[1]
        
        np.place(newnum, exp, newndval)

    # Export new raster
    obj_to_rst(newnum, out, gtrans, epsg, noData=ndval)

    return out


def floatrst_to_intrst(in_rst, out_rst):
    """
    Raster with float data to Raster with Integer Values
    """

    from glass.prop.img import get_nd

    nds = {
        'int8' : -128, 'int16' : -32768, 'int32' : -2147483648,
        'uint8' : 255, 'uint16' : 65535, 'uint32' : 4294967295
    }

    # Open Raster
    img = gdal.Open(in_rst)

    # Raster to Array
    rstnum = img.ReadAsArray()

    gtrans = img.GetGeoTransform()
    epsg = rst_epsg(img)

    # Round data
    rstint = np.around(rstnum, decimals=0)

    # Get min and max
    tstmin = rstint.min()
    tstmax = rstint.max()

    try:
        nd = int(round(get_nd(img), 0))
    except:
        nd = None

    if tstmin == nd:
        np.place(rstint, rstint == nd, np.nan)
        rstmin = rstint.min()
        rstmax = tstmax
    else:
        rstmin = tstmin
    
        if tstmax == nd:
            np.place(rstint, rstint == nd, np.nan)
            rstmax = rstint.max()
        else:
            rstmax = tstmax
    
    # Get dtype for output raster
    if rstmin < 0:
        if rstmin <= -128:
            if rstmin <= -32768:
                tmin = 'int32'
            else:
                tmin = 'int16'
        else:
            tmin = 'int8'
    else:
        tmin = 'u'
    
    if tmin == 'u':
        if rstmax >= 255:
            if rstmax >= 65535:
                tmax = 'uint32'
            else:
                tmax = 'uint16'
        else:
            tmax = 'uint8'

    else:
        if tmin == 'int8':
            if rstmax >= 127:
                if rstmax >= 32767:
                    tmax = 'int32'
                else:
                    tmax = 'int16'
            else:
                tmax = 'int8'
    
        elif tmin == 'int16':
            if rstmax >= 32767:
                tmax = 'int32'
            else:
                tmax = 'int16'
        else:
            tmax = 'int32'
    
    if tmax == 'int8':
        nt = np.int8
    elif tmax == 'int16':
        nt = np.int16
    elif tmax == 'int32':
        nt = np.int32
    elif tmax == 'uint8':
        nt = np.uint8
    elif tmax == 'uint16':
        nt = np.uint16
    else:
        nt = np.uint32
    
    # Get nodata for new raster
    new_nd = nds[tmax]
    
    # Place NoData value
    np.nan_to_num(rstint, copy=False, nan=new_nd)

    # Convert array type to integer
    rstint = rstint.astype(nt)

    # Export result to file and return
    return obj_to_rst(rstint, out_rst, gtrans, epsg, noData=new_nd)



def force_dtype(indata:list[str], outdtype:str, ndval:int|float, outfolder:str, file_format:str|None='.tif', refrst:str|None=None) -> list[str]:
    """
    Force a certain data type - convert data to it
    use grass gis

    indata could be a list of files or a list of folders
    """

    from glass.pys.oss  import lst_ff
    from glass.wenv.grs import grass_session
    from glass.pys.tm   import now_as_str
    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.rst.alg  import grsrstcalc

    refdt = {
        'Byte' : 'int', 'Int16' : 'int', 'Int32' : 'int',
        'UInt16' : 'int', 'UInt32' : 'int',
        'Float32' : 'double', 'Float64' : 'double'
    }

    # Create GRASS GIS Session
    loc = f"loc_{now_as_str(utc=True)}"
    ref = indata[0] if not refrst else refrst
    gb = grass_session(outfolder, loc=loc, srs=ref)

    res = []

    fform = '.tif' if not file_format else \
        file_format if file_format[0] == 0 else f'.{file_format}'

    for rst in indata:
        # Import raster
        grst = rst_to_grs(rst)

        # Convert
        nrst = grsrstcalc(f'{refdt[outdtype]}({grst})', f'{grst}_{outdtype}')

        # Export
        ntif = grs_to_rst(nrst, os.path.join(outfolder, f'{grst}{fform}'), dtype=outdtype, nodata=ndval)

        res.append(ntif)
    
    return res

