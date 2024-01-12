"""
Any type of data to raster
"""

import numpy as np

from osgeo import gdal, osr

"""
Feature Class to Raster
"""

def grsshp_to_grsrst(inshp, src, outrst, cmd=None):
    """
    GRASS Vector to GRASS Raster

    api:
    * pygrass
    * grass

    Vectorial geometry to raster
    
    If source is None, the convertion will be based on the cat field.
    
    If source is a string, the convertion will be based on the field
    with a name equal to the given string.
    
    If source is a numeric value, all cells of the output raster will have
    that same value.
    """

    __USE = "cat" if not src else "attr" if type(src) == str \
        else "val" if type(src) == int or \
            type(src) == float else None
    
    if not __USE:
        raise ValueError('\'source\' parameter value is not valid')
    
    if not cmd:
        from grass.pygrass.modules import Module
            
        m = Module(
            "v.to.rast", input=inshp, output=outrst, use=__USE,
            attribute_column=src if __USE == "attr" else None,
            value=src if __USE == "val" else None,
            overwrite=True, run_=False, quiet=True
        )
            
        m()
    
    else:
        from glass.pys import execmd

        ac_val = "" if __USE == "cat" else f" attribute_column={src}" \
            if __USE == "attr" else f" val={src}"
            
        rcmd = execmd((
            f"v.to.rast input={inshp} output={outrst} "
            f"use={__USE}{ac_val} --overwrite --quiet"
        ))

    return outrst


def shp_to_rst(shp, inSource, cellsize, nodata, outRaster, epsg=None,
               rst_template=None, snapRst=None, lyrname=None, api='pygdal',
               rtype=None, dtype=None):
    """
    Feature Class to Raster
    
    cellsize will be ignored if rst_template is defined
    
    * API's Available:
    - pygdal;
    - gdal;
    - pygrass;
    - grass;
    """
    
    if api == 'pygdal':
        from osgeo         import gdal, ogr
        from glass.prop.df import drv_name
    
        if not epsg:
            from glass.prop.prj import shp_ref

            srs = shp_ref(shp).ExportToWkt()
        else:
            from glass.prop.prj import epsg_to_wkt
            srs = epsg_to_wkt(epsg)
    
        # Get Extent
        dtShp = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = dtShp.GetLayer()
    
        if not rst_template:
            if not snapRst:
                x_min, x_max, y_min, y_max = lyr.GetExtent()
                x_res = int((x_max - x_min) / cellsize)
                y_res = int((y_max - y_min) / cellsize)
            
            else:
                from glass.prop.rst import adjust_ext_to_snap
                
                x_min, y_max, y_res, x_res, cellsize = adjust_ext_to_snap(
                    shp, snapRst
                )
    
        else:
            from glass.rd.rst import rst_to_array
        
            img_temp = gdal.Open(rst_template)
            geo_transform = img_temp.GetGeoTransform()
        
            y_res, x_res = rst_to_array(rst_template).shape
    
        # Create output
        dtRst = gdal.GetDriverByName(drv_name(outRaster)).Create(
            outRaster, x_res, y_res, gdal.GDT_Byte
        )
    
        if not rst_template:
            dtRst.SetGeoTransform((x_min, cellsize, 0, y_max, 0, -cellsize))
    
        else:
            dtRst.SetGeoTransform(geo_transform)
        
        dtRst.SetProjection(str(srs))
    
        bnd = dtRst.GetRasterBand(1)
        bnd.SetNoDataValue(nodata)
    
        gdal.RasterizeLayer(dtRst, [1], lyr, burn_values=[1])
    
        del lyr
        dtShp.Destroy()
    
    elif api == "gdal":
        from glass.pys      import execmd
        from glass.prop.df  import drv_name
        from glass.prop.ext import get_ext
        from glass.prop.rst import rst_fullprop

        if rst_template:
            ext, csize, _ = rst_fullprop(rst_template)

            left, right, bottom, top = ext

            cwidth, cheight = csize[0] if not cellsize else cellsize, \
                csize[1] if not cellsize else cellsize 
        
        else:
            left, right, bottom, top = get_ext(shp, geolyr=lyrname)

            cwidth, cheight = cellsize, cellsize

        __use = f"-a {inSource}" if type(inSource) == str else \
            f"-burn {str(inSource)}" if type(inSource) == float \
                or type(inSource) == int else "-burn 1"
        
        lyr = f" -l {lyrname}" if lyrname else ""

        predictor = "1" if not rtype else "2" if rtype==int else \
            "3" if rtype==float else "1"
        
        if not dtype:
            ot = " -ot UInt16" if rtype == int else " -ot Float64"
        
        else:
            ot = f" -ot {dtype}"

        opt = (
            f"-co COMPRESS=LZW -co PREDICTOR={predictor} "
            "-co TILED=YES -co BIGTIFF=IF_NEEDED -co TFW=YES"
        )

        cmd = (
            f"gdal_rasterize -of {drv_name(outRaster)} "
            f"-a_nodata {str(nodata)}{lyr} {__use} "
            f"-te {str(left)} {str(bottom)} {str(right)} {str(top)} "
            f"-tr {str(cwidth)} {str(cheight)} "
            f"{shp} {outRaster} {opt}{ot}"
        )

        rcmd = execmd(cmd)
    
    elif api == 'grass' or api == 'pygrass':
        """
        Use GRASS GIS
        - Start Session
        - Import data
        - Convert
        - Export
        """
        
        import os
        from glass.pys.oss  import fprop
        from glass.wenv.grs import run_grass
        from glass.prop.prj import get_epsg

        # Create GRASS GIS Session
        ws = os.path.dirname(outRaster)
        loc = fprop(outRaster, 'fn')
        epsg = get_epsg(shp)

        gbase = run_grass(ws, location=loc, srs=epsg)

        import grass.script.setup as gsetup

        gsetup.init(gbase, ws, loc, 'PERMANENT')

        # Import Packages
        from glass.it.shp   import shp_to_grs
        from glass.it.rst   import grs_to_rst
        from glass.wenv.grs import shp_to_region

        # Shape to GRASS GIS
        gshp = shp_to_grs(shp, asCMD=True)

        # Set Region
        shp_to_region(gshp, cellsize)

        # Convert
        grst = grsshp_to_grsrst(gshp, inSource, f"{gshp}__rst", api="grass")

        # Export
        grs_to_rst(grst, outRaster, as_cmd=True)
    
    else:
        raise ValueError(f'API {api} is not available')
    
    return outRaster


def shape_to_rst_wShapeCheck(inShp, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Feature Class to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    import os
    from glass.pys      import obj_to_lst
    from glass.prop.rst import rst_shape
    
    desiredCellsizes = obj_to_lst(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    workspace = os.path.dirname(outRst)
    
    RASTERS = [shp_to_rst(
        inShp, None, cellsize, -1, os.path.join(
            workspace, f'tst_cell_{str(cellsize)}.tif'
        ), inEPSG, api='pygdal'
    ) for cellsize in desiredCellsizes]
    
    tstShape = rst_shape(RASTERS)
    
    for rst in tstShape:
        NCELLS = tstShape[rst][0] * tstShape[rst][1]
        tstShape[rst] = NCELLS
    
    NICE_RASTER = None
    for i in range(len(desiredCellsizes)):
        if tstShape[RASTERS[i]] <= maxCellNumber:
            NICE_RASTER = RASTERS[i]
            break
        
        else:
            continue
    
    if not NICE_RASTER:
        return None
    
    else:
        os.rename(NICE_RASTER, outRst)
        
        for rst in RASTERS:
            if os.path.isfile(rst) and os.path.exists(rst):
                os.remove(rst)
        
        return outRst


"""
Extent to Raster
"""

def ext_to_rst(topLeft, btRight, outRst,
               cellsize=None, epsg=None, outEpsg=None,
               invalidResultAsNull=None, rstvalue=None):
    """
    Extent to Raster
    """
    
    from osgeo import gdal_array

    from glass.prop.df  import drv_name
    from glass.prop.rst import compress_option
    from glass.prop.prj import epsg_to_wkt
    
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
    
    if outEpsg and not epsg:
        epsg = outEpsg
    
    # Get row and cols number
    rows = (float(top) - float(bottom)) / cellsize
    cols = (float(right) - float(left)) / cellsize
    
    rows = int(rows) if rows == int(rows) else int(rows) + 1
    cols = int(cols) if cols == int(cols) else int(cols) + 1

    # Get np.dtype
    if type(rstvalue) == int and rstvalue <= 1:
        _dtype = np.byte
    else:
        _dtype = None
    
    if not invalidResultAsNull:
        if not rstvalue:
            narray = np.zeros((rows, cols), dtype=np.byte)
        
        else:
            narray = np.full((rows, cols), rstvalue, dtype=_dtype)
    else:
        try:
            if not rstvalue:
                narray = np.zeros((rows, cols), dtype=np.byte)
            
            else:
                narray = np.full((rows, cols), rstvalue, dtype=_dtype)
        except:
            return None
    
    # Create new Raster
    drv  = drv_name(outRst)
    copt = compress_option(drv)

    if copt:
        img = gdal.GetDriverByName(drv).Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(narray.dtype),
            options=[copt]
        )
    
    else:
        img = gdal.GetDriverByName(drv).Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(narray.dtype)
        )
    
    img.SetGeoTransform((left, cellsize, 0, top, 0, -cellsize))
    
    band = img.GetRasterBand(1)
    
    band.WriteArray(narray)
    
    if epsg:
        img.SetProjection(epsg_to_wkt(epsg))
    
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

