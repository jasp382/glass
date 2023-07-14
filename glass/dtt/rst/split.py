"""
Split Raster's into tiles
"""



def nrsts_fm_rst(rst, rows, cols, out_fld, bname):
    """
    Split raster into several rasters

    The number of new rasters will be determined by the extent of the 
    raster and the maximum number of rows and cols that the new
    rasters could have.
    """

    import os
    from osgeo          import gdal
    from glass.prop.img import rst_epsg
    from glass.wt.rst   import ext_to_rst

    # Open Raster
    img = gdal.Open(rst, gdal.GA_ReadOnly)

    # Get EPSG
    epsg = rst_epsg(img)

    # Get raster cellsize
    tlx, csx, xr, tly, yr, csy = img.GetGeoTransform()

    # Get Raster cols and Rows
    rrows, rcols = img.RasterYSize, img.RasterXSize

    # Get Raster max X and min Y (bottom right)
    rmax_x = tlx + (rcols * csx)
    rmin_y = tly + (rrows * csy)

    # Get Number of rasters to be created
    nr_rows = int(rrows / rows)
    nr_rows = nr_rows if nr_rows == rrows / rows else nr_rows + 1
    nr_cols = int(rcols / cols)
    nr_cols = nr_cols if nr_cols == rcols / cols else nr_cols + 1

    # Create new rasters
    newrst = []
    for i in range(nr_rows):
        # TopLeft Y
        _tly = tly + ((rows * csy) * i)

        # BottomRight Y
        _bry = _tly + (csy * rows)

        # If fishnet min y is lesser than raster min_y
        # Use raster min_y
        if _bry < rmin_y:
            _bry = rmin_y
        
        for e in range(nr_cols):
            # TopLeft X
            _tlx = tlx + ((cols * csx) * e)

            # Bottom Right X
            _brx = _tlx + (csx * cols)

            # If fishnet max x is greater than raster max_x
            # Use raster max_x
            if _brx > rmax_x:
                _brx = rmax_x
            
            # Create Raster
            nrst = ext_to_rst(
                (_tlx, _tly), (_brx, _bry),
                os.path.join(out_fld, f"{bname}_{str(i)}{str(e)}.tif"),
                cellsize=csx, epsg=epsg, rstvalue=1
            )

            newrst.append(nrst)
    
    return newrst

