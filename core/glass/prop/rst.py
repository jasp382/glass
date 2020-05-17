"""
Get Raster properties
"""

def compress_option(drv):
    """
    Return compress option for some gdal driver
    """

    if drv == 'GTiff':
        return 'COMPRESS=LZW'
    else:
        return None


def rst_dtype(rst):
    """
    Return Type of Raster Dataset

    return numpy class
    """

    from osgeo import gdal, gdal_array

    img = gdal.Open(rst, gdal.GA_ReadOnly)

    bnd = img.GetRasterBand(1).DataType

    return gdal_array.GDALTypeCodeToNumericTypeCode(bnd)


def rst_ext(rst):
    """
    Return a array with the extent of one raster dataset
    
    array order = Xmin (left), XMax (right), YMin (bottom), YMax (top)
    """
    
    from osgeo import gdal
        
    img = gdal.Open(rst)
        
    lnhs = int(img.RasterYSize)
    cols = int(img.RasterXSize)
        
    left, cellx, z, top, c, celly = img.GetGeoTransform()
        
    right  = left + (cols * cellx)
    bottom = top  - (lnhs * abs(celly))
        
    extent = [left, right, bottom, top]
    
    return extent


def rst_shape(rst):
    """
    Return number of lines and columns in a raster
    """
    
    from glass.pys    import obj_to_lst
    from glass.rd.rst import rst_to_array
    
    rst    = obj_to_lst(rst)
    shapes = {}
        
    for r in rst:
        array     = rst_to_array(r)
        lnh, cols = array.shape
            
        shapes[r] = [lnh, cols]
            
        del array
    
    return shapes if len(rst) > 1 else shapes[rst[0]]


def get_cellsize(rst, xy=False, bnd=None, gisApi='gdal'):
    """
    Return cellsize of one or more Raster Datasets
    
    In the case of groups, the result will be:
    d = {
        'path_to_raster1': cellsize_raster_1,
        'path_to_raster2': cellsize_raster_2,
        'path_to_raster3': cellsize_raster_3,
        ...,
        'path_to_rastern': cellsize_raster_n,
    }
    
    API'S Available:
    * gdal;
    * pygrass
    """
    
    import os
    
    if gisApi == 'gdal':
        from osgeo            import gdal
        from glass.prop.img import get_cell_size

        if type(rst) != list:
            if os.path.exists(rst) and os.path.isdir(rst):
                from glass.pys.oss import lst_ff
                from glass.prop  import raster_formats

                rsts = lst_ff(rst, file_format=raster_formats())
            
            elif os.path.exists(rst) and os.path.isfile(rst):
                rsts = [rst]
            else:
                raise ValueError((
                    'Invalid object rst. Please insert a path to a raster, '
                    'a path to a directory with rasters or a list with '
                    'rasters path.'
                ))
        
        else:
            rsts = rst
        
        cs = {}
        for r in rsts:
            imgsrc = gdal.Open(r)

            cs[r] = get_cell_size(
                imgsrc) if xy else get_cell_size(imgsrc)[0]
        
        return cs[rsts[0]] if len(rsts) == 1 else cs
    
    elif gisApi == 'qgis':
        from qgis.core import QgsRasterLayer
        
        rasterLyr = QgsRasterLayer(rst, "lyr")
        x = rasterLyr.rasterUnitsPerPixelX()
        
        if xy:
            y = rasterLyr.rasterUnitsPerPixelY()
            
            return x, y
        else:
            return x
    
    elif gisApi == 'pygrass':
        import grass.script as grass
        
        dic = grass.raster.raster_info(rst)
        
        return dic['nsres']
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))


def get_cell_coord(line, column, xmin, ymax, cellwidth, cellheight):
    """
    Return x, y coordinates of one cell in a raster
    
    This method needs x, y of the top left corner because a numpy array
    have indexes that increses from left to right and from top to bottom
    """
    
    x = xmin + (column * cellwidth) + (cellwidth / 2)
    
    y = ymax - ( line * cellheight) - (cellheight / 2)
    
    return x, y


def get_cell_idx(array, x, y, xmin, ymax, cell_width, cell_height):
    """
    Given the position of a cell, return the row and column of that cell in
    one array
    """

    colIdx = int((x - xmin) / cell_width)
    rowIdx = int((ymax -y) / cell_height)

    return rowIdx, colIdx


def count_cells(raster, countNodata=None):
    """
    Return number of cells in a Raster Dataset
    """
    
    from glass.rd.rst import rst_to_array
    from glass.pys.num  import count_where
    
    a = rst_to_array(raster)
    
    lnh, col = a.shape
    nrcell   = lnh * col
    
    if countNodata:
        return nrcell
    
    else:
        NoDataValue = get_nodata(raster)
        NrNodata = count_where(a, a == NoDataValue)
        return nrcell - NrNodata


def get_nodata(r):
    """
    Returns the value defining NoData in a Raster file
    
    API'S Available:
    * gdal;
    """
    
    gisApi = 'gdal'
    
    if gisApi == 'gdal':
        from glass.prop.img import get_nd
        from osgeo import gdal
        
        img = gdal.Open(r)
        
        ndVal = get_nd(img)
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return ndVal


def rst_distinct(rst):
    """
    Export a list with the values of a raster
    
    API'S Available:
    * gdal;
    """
    
    import numpy
    from glass.rd.rst import rst_to_array
    
    v = numpy.unique(rst_to_array(rst, flatten=True, with_nodata=False))
    
    return list(v)

"""
Raster Statistics
"""

def rst_stats(rst, bnd=None):
    """
    Get Raster Statistics
    
    The output will be a dict with the following keys:
    * Min - Minimum
    * Max - Maximum
    * Mean - Mean value
    * StdDev - Standard Deviation
    """

    from osgeo import gdal
        
    r = gdal.Open(rst)
        
    bnd = r.GetRasterBand(1 if not bnd else bnd)
    stats = bnd.GetStatistics(True, True)
        
    dicStats = {
        'MIN' : stats[0], 'MAX' : stats[1], 'MEAN' : stats[2],
        "STDEV" : stats[3]
    }
    
    return dicStats


def frequencies(r, excludeNoData=True):
    """
    Return frequencies table
    """
    
    import numpy as np
    from osgeo            import gdal
    from glass.prop.img import get_nd
    
    if type(r).__name__ == 'str':
        img = gdal.Open(r)
        arr = img.ReadAsArray()
    elif type(r).__name__ == 'Dataset':
        img = r
        arr = img.ReadAsArray()
    else:
        img = None
        arr = r
    
    unique = list(np.unique(arr))
    
    one_arr = arr.reshape(arr.shape[0] * arr.shape[1])
    
    freq    = np.bincount(one_arr)
    freq    = freq[freq != 0]
    
    if excludeNoData:
        if type(r).__name__ == 'str' or type(r).__name__ == 'Dataset':
            ndval = get_nd(img)
            return {
                unique[i] : freq[i] for i in range(len(unique)) \
                    if unique[i] != ndval
            }
        
        else:
            return {unique[i] : freq[i] for i in range(len(unique))}
    else:
        return {unique[i] : freq[i] for i in range(len(unique))}


def get_percentage_value(rst, value, includeNodata=None):
    """
    Return the % of cells with a certain value
    """
    
    import numpy
    from osgeo                 import gdal
    from glass.pys.num         import count_where
    from glass.rd.rst    import rst_to_array
    from glass.prop.rst import get_nodata
    
    array = rst_to_array(rst)
    
    lnh, col = array.shape
    nrcell = lnh * col
    
    if not includeNodata:
        nd = get_nodata(rst, gisApi='gdal')
        
        nd_cells = count_where(array, array == nd)
        
        nrcell = nrcell - nd_cells
    
    valCount = count_where(array, array == value)
    
    perc = (valCount / float(nrcell)) * 100
    
    return perc


def percentage_nodata(rst):
    """
    Return the % of cells with nodata value
    """
    
    import numpy
    from glass.pys.num     import count_where
    from glass.rd.rst    import rst_to_array
    from glass.prop.rst import get_nodata
    
    array = rst_to_array(rst)
    
    lnh, col = array.shape
    nrcell = lnh * col
    
    nd = get_nodata(rst, gisApi='gdal')
    nd_cells = count_where(array, array == nd)
    
    perc = (nd_cells / float(nrcell)) * 100
    
    return perc


"""
Snap Raster 
"""

def adjust_ext_to_snap(outExt, snapRst):
    """
    Adjust extent for a output raster to snap with other raster
    """
    
    from glass.prop     import is_shp, check_isRaster
    from glass.prop.rst import rst_ext, get_cellsize
    from glass.gobj     import new_pnt, create_polygon
    
    # Check if outExt is a raster or not
    isRst = check_isRaster(outExt)
    
    if isRst:
        shpAExt = rst_ext(outExt)
    
    else:
        isShp = is_shp(outExt)
        
        if isShp:
            from glass.prop.feat import get_ext
            
            shpAExt = get_ext(outExt)
        
        else:
            raise ValueError((
                "outExt value should be a path to a SHP or to a Raster file"
            ))
    
    # Check if snapRst is a raster
    isRst = check_isRaster(snapRst)
    
    if not isRst:
        raise ValueError((
            "snapRst should be a path to a raster file"
        ))
    
    # Get snapRst Extent
    snapRstExt = rst_ext(snapRst)
    
    # Get cellsize
    csize = get_cellsize(snapRst)
    
    # Find extent point of outExt inside the two extents
    # This will be used as pseudo origin
    
    snapRstPnt = [
        new_pnt(snapRstExt[0], snapRstExt[3]),
        new_pnt(snapRstExt[1], snapRstExt[3]),
        new_pnt(snapRstExt[1], snapRstExt[2]),
        new_pnt(snapRstExt[0], snapRstExt[2]),
        new_pnt(snapRstExt[0], snapRstExt[3]),
    ]
    
    poly_snap_rst = create_polygon(snapRstPnt)
    
    outExtPnt = {
        'top_left'     : new_pnt(shpAExt[0], shpAExt[3]),
        'top_right'    : new_pnt(shpAExt[1], shpAExt[3]),
        'bottom_right' : new_pnt(shpAExt[1], shpAExt[2]),
        'bottom_left'  : new_pnt(shpAExt[0], shpAExt[2])
    }
    
    out_rst_pseudo = {}
    for pnt in outExtPnt:
        out_rst_pseudo[pnt] = outExtPnt[pnt].Intersects(poly_snap_rst)
    
    pseudoOrigin = outExtPnt['top_left'] if out_rst_pseudo['top_left'] else \
        outExtPnt['bottom_left'] if out_rst_pseudo['bottom_left'] else \
        outExtPnt['top_right'] if out_rst_pseudo['top_right'] else \
        outExtPnt['bottom_right'] if out_rst_pseudo['bottom_right'] else None
        
    if not pseudoOrigin:
        raise ValueError((
            'Extents doesn\'t have overlapping areas'
        ))
    
    pseudoOriginName = 'top_left' if out_rst_pseudo['top_left'] else \
        'bottom_left' if out_rst_pseudo['bottom_left'] else \
        'top_right' if out_rst_pseudo['top_right'] else \
        'bottom_right' if out_rst_pseudo['bottom_right'] else None
    
    # Get out Raster Shape
    n_col = int((shpAExt[1] - shpAExt[0]) / csize)
    n_row = int((shpAExt[3] - shpAExt[2]) / csize)
    
    # Get Output Raster real origin/top left
    yName, xName = pseudoOriginName.split('_')
    
    if xName == 'left':
        # Obtain left of output Raster
        left_out_rst = snapRstExt[0] + (
            csize * int((shpAExt[0] - snapRstExt[0]) / csize))
    
    else:
        # obtain right of output Raster
        right_out_rst = snapRstExt[1] - (
            csize * int((snapRstExt[1] - shpAExt[1]) / csize))
        
        # Use right to obtain left coordinate
        left_out_rst = right_out_rst - (n_col * csize)
    
    if yName == 'top':
        # Obtain top of output Raster
        top_out_rst = snapRstExt[3] - (
            csize * int((snapRstExt[3] - shpAExt[3]) / csize))
        
    else:
        # obtain bottom of output raster
        bot_out_rst = snapRstExt[2] + (
            csize * int((shpAExt[2] - snapRstExt[2]) / csize))
        
        # use bottom to find the top of the output raster
        top_out_rst = bot_out_rst + (n_row * csize)
        
    return left_out_rst, top_out_rst, n_row, n_col, csize


"""
Get Raster properties by using GRASS GIS tools
"""

def raster_report(rst, rel, _units=None, ascmd=None):
    """
    Units options:
    * Options: mi, me, k, a, h, c, p
    ** mi: area in square miles
    ** me: area in square meters
    ** k: area in square kilometers
    ** a: area in acres
    ** h: area in hectares
    ** c: number of cells
    ** p: percent cover
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        report = Module(
            "r.report", map=rst, flags="h", output=rel,
            units=_units, run_=False, quiet=True
        )
    
        report()
    
    else:
        from glass.pys import obj_to_lst, execmd
        
        rcmd = execmd("r.report map={} output={}{} -h".format(
            rst, rel,
            " units={}".format(",".join(obj_to_lst(_units))) if _units else ""
        ))
    
    return rel


def sanitize_report(report):
    """
    Retrieve data from Report of a Raster
    """
    
    import codecs
    
    with codecs.open(report, 'r') as txt:
        rows = [lnh for lnh in txt]
        __rows = []
        l = [" ", "category", "."]
        
        c = 1
        for r in rows:
            if c <= 4:
                c += 1
                continue
            
            _r =  r.strip("\n")
            _r = _r.strip("|")
            
            for i in l:
                _r = _r.replace(i, "")
            
            _r = _r.replace(";", "|")
            
            __rows.append(_r.split("|"))
        
        __rows[0] = ['0', '1', '1'] + __rows[0][3:]
        
        return __rows[:-4]


def san_report_combine(report):
    from glass.rd     import tbl_to_obj
    from glass.pd.fld import splitcol_to_newcols
    
    repdata = tbl_to_obj(report, _delimiter="z")
    
    repdata.rename(columns={repdata.columns.values[0] : 'data'}, inplace=True)
    repdata.drop([
        0, 1, 2, 3, repdata.shape[0]-1, repdata.shape[0]-2,
        repdata.shape[0]-3, repdata.shape[0]-4
    ], axis=0, inplace=True)
    
    repdata["data"] = repdata.data.str.replace(
        ' ', '').str.replace('.', '').str.replace(
            'category', '').str.replace(
                "Category", '').str.replace(';', '|')
    
    repdata["data"] = repdata.data.str[1:-1]
    
    repdata = splitcol_to_newcols(repdata, "data", "|", {
        0 : "new_value", 1 : "first_raster_val",
        2 : "second_raster_val", 3 : "n_cells"
    })
    
    return repdata


def get_rst_report_data(rst, UNITS=None):
    """
    Execute r.report and get reported data
    """
    
    import os
    from glass.pys.char import random_str
    from glass.pys.oss  import del_file
    
    REPORT_PATH = raster_report(rst, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "{}.txt".format(random_str(6))
    ), _units=UNITS)
    
    report_data = sanitize_report(REPORT_PATH)
    
    del_file(REPORT_PATH)
    
    return report_data

