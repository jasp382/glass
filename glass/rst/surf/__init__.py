"""
Surface tools for Raster
"""

import os

from glass.wenv.grs import grass_session


"""
Terrain
"""


def slope_aspect(dem, slope_rst=None, aspect_rst=None, api="grass",
                slope_units="degrees", aspe_fromnorth=True, ws=None):
    """
    Generate Slope and Aspect Rasters from
    Digital Elevation Model
    """

    from glass.pys.oss import fprop, mkdir
    from glass.pys.tm import now_as_str

    if not slope_rst and not aspect_rst:
        bname      = fprop(dem, 'fn')
        slope_rst  = os.path.join(os.path.dirname(dem), f'{bname}_slope.tif')
        aspect_rst = os.path.join(os.path.dirname(dem), f'{bname}_aspect.tif')
    
    # Create GRASS GIS session
    gws = mkdir(os.path.join(
        os.path.dirname(dem),
        now_as_str(utc=True)
    )) if not ws else ws
    
    loc = 'surface_loc' if not ws else now_as_str(utc=True)

    # Create GRASS GIS Location
    gb = grass_session(gws, loc=loc, srs=dem)

    # Import GRASS GIS methods
    from glass.it.rst import rst_to_grs, grs_to_rst
    from glass.rst.surf.grs import slope, aspect

    # Import dem
    grs_dem = rst_to_grs(dem, as_cmd=True)

    # Run Slope and Aspect
    grs_slope = None if not slope_rst else slope(
        grs_dem, fprop(slope_rst, 'fn'),
        data=slope_units, api=api
    )

    grs_aspec = None if not aspect_rst else aspect(
        grs_dem, fprop(aspect_rst, 'fn'),
        from_north=True if aspe_fromnorth else None,
        api=api
    )

    oslope = None if not grs_slope else grs_to_rst(
        grs_slope, slope_rst,
        dtype="Float64"
    )

    oaspec = None if not grs_aspec else grs_to_rst(
        grs_aspec, aspect_rst,
        dtype="Float64"
    )

    if oslope and oaspec:
        return oslope, oaspec
    elif oslope and not oaspec:
        return oslope
    else:
        return oaspec


def gdal_slope(dem, srs, slope, unit='DEGREES'):
    """
    Create Slope Raster
    
    TODO: Test and see if is running correctly
    """
    
    import numpy    
    import math
    from scipy.ndimage  import convolve
    from glass.rd.rst   import rst_to_array
    from glass.wt.rst   import obj_to_rst
    from glass.prop.rst import rst_cellsize, get_nodata, rst_geoprop
    from glass.prop.prj import rst_epsg
    
    # ################ #
    # Global Variables #
    # ################ #
    cellsize = rst_cellsize(dem, gisApi='gdal')
    # Get Nodata Value
    NoData = get_nodata(dem)

    # EPSG
    epsg = rst_epsg(dem)

    # Geo Parameters
    left, cellx, top, celly = rst_geoprop(dem)
    gtrans = (left, cellx, 0, top, 0, celly)
    
    # #################### #
    # Produce Slope Raster #
    # #################### #
    # Get Elevation array
    arr_dem = rst_to_array(dem)
    # We have to get a array with the number of nearst cells with values
    with_data = numpy.zeros((arr_dem.shape[0], arr_dem.shape[1]))
    numpy.place(with_data, arr_dem!=NoData, 1.0)
    mask = numpy.array([[1,1,1],
                        [1,0,1],
                        [1,1,1]])
    arr_neigh = convolve(with_data, mask, mode='constant')
    numpy.place(arr_dem, arr_dem==NoData, 0.0)
    # The rate of change in the x direction for the center cell e is:
    # TODO: update slope formula
    # TODO: is right less left and not left less right
    kernel_dz_dx_left = numpy.array([[0,0,1],
                                     [0,0,2],
                                     [0,0,1]])
    kernel_dz_dx_right = numpy.array([[1,0,0],
                                     [2,0,0],
                                     [1,0,0]])
    dz_dx = (convolve(arr_dem, kernel_dz_dx_left, mode='constant')-convolve(arr_dem, kernel_dz_dx_right, mode='constant')) / (arr_neigh * cellsize)
    # The rate of change in the y direction for cell e is:
    kernel_dz_dy_left = numpy.array([[0,0,0],
                                    [0,0,0],
                                    [1,2,1]])
    kernel_dz_dy_right = numpy.array([[1,2,1],
                                    [0,0,0],
                                    [0,0,0]])
    dz_dy = (convolve(arr_dem, kernel_dz_dy_left, mode='constant')-convolve(arr_dem, kernel_dz_dy_right, mode='constant')) / (arr_neigh * cellsize)
    # Taking the rate of change in the x and y direction, the slope for the center cell e is calculated using
    rise_run = ((dz_dx)**2 + (dz_dy)**2)**0.5
    if unit=='DEGREES':
        arr_slope = numpy.arctan(rise_run) * 57.29578
    elif unit =='PERCENT_RISE':
        arr_slope = numpy.tan(numpy.arctan(rise_run)) * 100.0
    # Estimate the slope for the cells with less than 8 neigh
    aux_dem = rst_to_array(dem)
    index_vizinhos = numpy.where(arr_neigh<8)
    for idx in range(len(index_vizinhos[0])):
        # Get Value of the cell
        lnh = index_vizinhos[0][idx]
        col = index_vizinhos[1][idx]
        e = aux_dem[lnh][col]
        a = aux_dem[lnh-1][col-1]
        if a == NoData:
            a = e
        if lnh==0 or col==0:
            a=e
        b = aux_dem[lnh-1][col]
        if b == NoData:
            b = e
        if lnh==0:
            b=e
        try:
            c = aux_dem[lnh-1][col+1]
            if c == NoData:
                c=e
            if lnh==0:
                c=e
        except:
            c = e
        d = aux_dem[lnh][col-1]
        if d == NoData:
            d = e
        if col==0:
            d=e
        try:
            f = aux_dem[lnh][col+1]
            if f == NoData:
                f=e
        except:
            f=e
        try:
            g = aux_dem[lnh+1][col-1]
            if g == NoData:
                g=e
            if col==0:
                g=e
        except:
            g=e
        try:
            h = aux_dem[lnh+1][col]
            if h ==NoData:
                h = e
        except:
            h=e
        try:
            i = aux_dem[lnh+1][col+1]
            if i == NoData:
                i = e
        except:
            i=e
        dz_dx = ((c + 2*f + i) - (a + 2*d + g)) / (8 * cellsize)
        dz_dy = ((g + 2*h + i) - (a + 2*b + c)) / (8 * cellsize)
        rise_sun = ((dz_dx)**2 + (dz_dy)**2)**0.5
        if unit == 'DEGREES':
            arr_slope[lnh][col] = math.atan(rise_sun) * 57.29578
        elif unit == 'PERCENT_RISE':
            arr_slope[lnh][col] = math.tan(math.atan(rise_sun)) * 100.0
    # Del value originally nodata
    numpy.place(arr_slope, aux_dem==NoData, numpy.nan)
    #arr_slope[lnh][col] = slope_degres
    obj_to_rst(arr_slope, slope, gtrans, epsg, noData=NoData)


