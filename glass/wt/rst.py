"""
Data to Raster File
"""

import numpy as np
from osgeo import gdal, osr, gdal_array

from glass.prop.df import drv_name

"""
Array to Raster
"""

def obj_to_rst(inArray, outRst, geotrans, epsg, noData=None):
    """
    Send Array to Raster

    inArray - array of array with raster date
    outRst - path to output raster file - 
        inArray will be written in this file
    """
    
    from glass.prop.rst import compress_option
    from glass.prop.prj import epsg_to_wkt
    
    rows, cols = inArray.shape
    drv_n      = drv_name(outRst)
    driver     = gdal.GetDriverByName(drv_n)

    c_opt = compress_option(drv_n)
    if c_opt:
        out = driver.Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype),
            options=[c_opt]
        )
    else:
        out = driver.Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype)
        )
    
    out.SetGeoTransform(geotrans)

    outBand = out.GetRasterBand(1)
    
    if noData or noData==0:
        outBand.SetNoDataValue(noData)
        
    outBand.WriteArray(inArray)
    
    out.SetProjection(epsg_to_wkt(epsg))
    
    outBand.FlushCache()
    
    return outRst


def rst_from_origin(topleft, shape, cellsize, rst, epsg):
    """
    Create Raster with a certain origin, shape and cellsize
    """

    # GeoTransform Parameters
    left, top = topleft
    nrows, ncols = shape
    cellx, celly = cellsize

    res = np.ones((nrows, ncols))

    # Export
    gtrans = (left, cellx, 0, top, 0, celly)

    obj_to_rst(res, rst, gtrans, epsg)

    return rst


"""
Extent to Raster
"""

def ext_to_rst(topLeft, btRight, outRst,
               cellsize=None, epsg=None, outEpsg=None,
               invalidResultAsNull=None, rstvalue=None):
    """
    Extent to Raster
    """
    
    from glass.prop.df import drv_name
    
    left, top     = topLeft
    right, bottom = btRight
    
    cellsize = 10 if not cellsize else cellsize
    
    if outEpsg and epsg and outEpsg != epsg:
        from glass.gobj    import new_pnt
        from glass.gobj    import create_polygon
        from glass.prj.obj import prj_ogrgeom
        
        extGeom = prj_ogrgeom(create_polygon([
            new_pnt(left, top), new_pnt(right, top),
            new_pnt(right, bottom), new_pnt(left, bottom), new_pnt(left, top)
        ]), epsg, outEpsg)

        epsg = outEpsg
        
        left, right, bottom, top = extGeom.GetEnvelope()
    
    # Get row and cols number
    rows = (float(top) - float(bottom)) / cellsize
    cols = (float(right) - float(left)) / cellsize
    
    rows = int(rows) if rows == int(rows) else int(rows) + 1
    cols = int(cols) if cols == int(cols) else int(cols) + 1
    
    if not invalidResultAsNull:
        if not rstvalue:
            NEW_RST_ARRAY = np.zeros((rows, cols))
        
        else:
            NEW_RST_ARRAY = np.full((rows, cols), rstvalue)
    else:
        try:
            if not rstvalue:
                NEW_RST_ARRAY = np.zeros((rows, cols))
            
            else:
                NEW_RST_ARRAY = np.full((rows, cols), rstvalue)
        except:
            return None
    
    # Create new Raster
    img = gdal.GetDriverByName(drv_name(outRst)).Create(
        outRst, cols, rows, 1, gdal.GDT_Byte
    )
    
    img.SetGeoTransform((left, cellsize, 0, top, 0, -cellsize))
    
    band = img.GetRasterBand(1)
    
    band.WriteArray(NEW_RST_ARRAY)
    
    if epsg:
        rstSrs = osr.SpatialReference()
        rstSrs.ImportFromEPSG(epsg)
        img.SetProjection(rstSrs.ExportToWkt())
    
    band.FlushCache()
    
    return outRst


def rstext_to_rst(inrst, outrst, cellsize=None, epsg=None, rstval=None):
    """
    Raster Extent to Raster
    """

    from glass.prop.rst import rst_ext, get_cellsize

    # Get Raster Extent
    left, right, bottom, top = rst_ext(inrst)

    # GET EPSG
    if not epsg:
        from glass.prop.prj import rst_epsg

        epsg = rst_epsg(inrst)
    
    # Create raster
    ext_to_rst(
        (left, top), (right, bottom), outrst,
        cellsize=get_cellsize(inrst) if not cellsize else cellsize,
        epsg=epsg, rstvalue=rstval
    )

    return outrst


def shpext_to_rst(inShp, outRaster, cellsize=None, epsg=None,
                  invalidResultAsNone=None, outEpsg=None):
    """
    Extent to raster
    
    if invalidResultAsNone - if for some reason something went wrong, the 
    result of this method will be a None Object if there is an error on the
    numpy array creation. If False, an error will be raised.
    """
    
    import geopandas as gp
    from glass.prop.ext import get_ext, get_dfext
        
    cellsize = 10 if not cellsize else cellsize

    if not epsg:
        from glass.prop.prj import get_epsg

        _epsg = get_epsg(inShp)
    
    else:
        _epsg = epsg
    
    # Get extent
    if type(inShp) == gp.GeoDataFrame:
        left, right, bottom, top = get_dfext(inShp, 'geometry')
    
    else:
        try:
            left, right, bottom, top = get_ext(inShp)
        except:
            left, right, bottom, top = inShp.GetEnvelope()
    
    return ext_to_rst(
        (left, top), (right, bottom), outRaster,
        cellsize=cellsize, epsg=_epsg, outEpsg=outEpsg,
        invalidResultAsNull=invalidResultAsNone
    )


def geomext_to_rst_wShapeCheck(inGeom, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Geometry to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    from glass.pys import obj_to_lst
    
    desiredCellsizes = obj_to_lst(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    # Get geom extent
    left, right, bottom, top = inGeom.GetEnvelope()
    
    # Check Rasters Shape for each desired cellsize
    SEL_CELLSIZE = None
    for cellsize in desiredCellsizes:
        # Get Row and Columns Number
        NROWS = int(round((top - bottom) / cellsize, 0))
        NCOLS = int(round((right - left) / cellsize, 0))
        
        NCELLS = NROWS * NCOLS
        
        if NCELLS <= maxCellNumber:
            SEL_CELLSIZE = cellsize
            break
    
    if not SEL_CELLSIZE:
        return None
    
    else:
        shpext_to_rst(
            inGeom, outRst, SEL_CELLSIZE, epsg=inEPSG,
            invalidResultAsNone=True
        )
        
        return outRst

