"""
Surface tools for Raster
"""

"""
Terrain
"""

def slope(demRst, slopeRst, data=None, api="pygrass"):
    """
    Get Slope Raster
    
    Data options:
    * percent;
    * degrees;
    """

    dataf = data if data == 'percent' or data == 'degrees' else 'degrees'

    if api == "pygrass":
        from grass.pygrass.modules import Module
    
        sl = Module(
            "r.slope.aspect", elevation=demRst, slope=slopeRst,
            format=dataf,
            overwrite=True, precision="FCELL", run_=False, quiet=True
        )
    
        sl()
    
    elif api == "grass":
        from glass.pyt import execmd
        
        rcmd = execmd((
            "r.slope.aspect elevation={} slope={} format={} "
            "precision=FCELL --overwrite --quiet"
        ).format(demRst, slopeRst, dataf))
    
    else:
        raise ValueError("API {} is not available".format(api))
    
    return slopeRst


def aspect(dem, rst_aspect, from_north=None, api="pygrass"):
    """
    Generate Aspect Raster
    """

    aspect_tmp = rst_aspect if not from_north else rst_aspect + '_normal'

    expression = None if not from_north else (
        "if({r} == 0, -1, if({r} < 90, 90 - {r}, 450 - {r}))"
    ).format(r=aspect_tmp)

    if api == 'pygrass':
        from gass.pygrass.modules import Module

        m = Module(
            "r.slope", elevation=dem, aspect=aspect_tmp,
            overwrite=True, precision="FCELL", run_=False, quiet=True
        )

        m()
    
    elif api == 'grass':
        from glass.pyt import execmd

        rcmd = execmd((
            "r.slope.aspect elevation={} aspect={} "
            "precision=FCELL --overwrite --quiet"
        ).format(dem, aspect_tmp))
    
    else:
        raise ValueError("API {} is not available".format(api))
    
    if from_north:
        from glass.geo.gt.nop.alg import rstcalc

        rrcmd = rstcalc(expression, rst_aspect, api=api)
    
    return rst_aspect


def gdal_slope(dem, srs, slope, unit='DEGREES'):
    """
    Create Slope Raster
    
    TODO: Test and see if is running correctly
    """
    
    import numpy;         import math
    from osgeo            import gdal
    from scipy.ndimage    import convolve
    from glass.geo.gt.fmrst    import rst_to_array
    from glass.geo.gt.torst    import obj_to_rst
    from glass.geo.gt.prop.rst import get_cellsize, get_nodata
    
    # ################ #
    # Global Variables #
    # ################ #
    cellsize = get_cellsize(dem, gisApi='gdal')
    # Get Nodata Value
    NoData = get_nodata(dem)
    
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
    obj_to_rst(arr_slope, slope, dem)


def viewshed(demrst, obsShp, output):
    """
    This tool computes a visibility analysis using observer points from
    a point shapefile.
    """
    
    import os
    from glass.pyt          import execmd
    from glass.pyt.oss      import fprop
    from glass.geo.gt.torst import saga_to_tif
    
    SAGA_RASTER = os.path.join(
        os.path.dirname(output),
        "sg_{}.sgrd".format(fprop(output, 'fn'))
    )
    
    cmd = (
       "saga_cmd ta_lighting 6 -ELEVATION {elv} -POINTS {pnt} "
       "-VISIBILITY {out} -METHOD 0"
    ).format(
        elv=demrst, pnt=obsShp, out=SAGA_RASTER
    )
    
    outcmd = execmd(cmd)
    
    # Convert to Tiif
    saga_to_tif(SAGA_RASTER, output)
    
    return output


def grs_viewshed(dem, obs_pnt, out_rst, max_dist=None, obs_elv=None):
    """
    Compute viewshed
    """
    
    from grass.pygrass.modules import Module
    
    vshd = Module(
        "r.viewshed", input=dem, output=out_rst,
        coordinates=obs_pnt,
        flags="b", overwrite=True, run_=False, quiet=True,
        max_distance=-1 if not max_dist else max_dist,
        observer_elevation=1.75 if not obs_elv else obs_elv
    )
    
    vshd()
    
    return out_rst

def thrd_viewshed(dem, pnt_obs, obs_id, out_folder):
    """
    Compute Viewshed for all points in pnt_obs using
    a multiprocessing approach
    """

    import os
    import multiprocessing as mp
    from glass.geo.gt.fmshp import shp_to_obj
    from glass.pyt.oss      import cpu_cores
    from glass.pyt.df.split import df_split
    from glass.geo.wenv.grs import run_grass
    
    # Points to DataFrame
    obs_df = shp_to_obj(pnt_obs)

    # Split DF by the number of cores
    n_cpu = cpu_cores()
    dfs   = df_split(obs_df, n_cpu)

    def run_viewshed_by_cpu(tid, obs, dem, output,
        vis_basename='vis', maxdst=None, obselevation=None):

        # Create GRASS GIS Session
        loc_name = 'loc_' + str(tid)
        gbase = run_grass(output, location=loc_name, srs=dem)

        # Start GRASS GIS Session
        import grass.script as grass
        import grass.script.setup as gsetup
        gsetup.init(gbase, output, loc_name, 'PERMANENT')

        from glass.geo.gt.torst    import rst_to_grs, grs_to_rst
        from glass.geo.gt.nop.surf import grs_viewshed

        # Send DEM to GRASS GIS
        grs_dem = rst_to_grs(dem, 'grs_dem', as_cmd=True)
    
        # Produce Viewshed for each point in obs
        for idx, row in obs.iterrows():
            vrst = grs_viewshed(
                grs_dem, (row.geometry.x, row.geometry.y),
                '{}_{}'.format(vis_basename, str(row[obs_id])),
                max_dist=maxdst, obs_elv=obselevation
            )
        
            frst = grs_to_rst(vrst, os.path.join(output, vrst + '.tif'))

    thrds = [mp.Process(
        target=run_viewshed_by_cpu, name='th-{}'.format(str(i+1)),
        args=(i+1, dfs[i], dem, out_folder,
            'vistoburn', 10000, 200)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    return out_folder


def thrd_viewshed_v2(dbname, dem, pnt_obs, obs_id):
    """
    Compute Viewshed for all points in pnt_obs using
    a multiprocessing approach
    """

    import os
    import pandas              as pd
    import numpy               as np
    from osgeo                 import gdal
    import multiprocessing     as mp
    from glass.geo.gt.fmshp    import shp_to_obj
    from glass.pyt.oss         import cpu_cores, mkdir
    from glass.pyt.df.split    import df_split
    from glass.geo.wenv.grs    import run_grass
    from glass.geo.gt.prop.prj import get_epsg_shp
    from glass.sql.to          import df_to_db
    from glass.pyt.oss         import del_file
    from glass.sql.db          import create_db
    
    # Get Work EPSG
    epsg = get_epsg_shp(pnt_obs)
    
    # Points to DataFrame
    obs_df = shp_to_obj(pnt_obs)

    # Split DF by the number of cores
    n_cpu = cpu_cores()
    dfs   = df_split(obs_df, n_cpu)

    def run_viewshed_by_cpu(tid, db, obs, dem, srs,
        vis_basename='vis', maxdst=None, obselevation=None):
        # Create Database
        new_db = create_db("{}_{}".format(db, str(tid)), api='psql')
        
        # Points to Database
        pnt_tbl = df_to_db(
            new_db, obs, 'pnt_tbl', api='psql', 
            epsg=srs, geomType='Point', colGeom='geometry')

        # Create GRASS GIS Session
        workspace = mkdir(os.path.join(
            os.path.dirname(dem), 'work_{}'.format(str(tid))
        ))
        loc_name = 'vis_loc'
        gbase = run_grass(workspace, location=loc_name, srs=dem)

        # Start GRASS GIS Session
        import grass.script as grass
        import grass.script.setup as gsetup
        gsetup.init(gbase, workspace, loc_name, 'PERMANENT')

        from glass.geo.gt.torst    import rst_to_grs, grs_to_rst
        from glass.geo.gt.nop.surf import grs_viewshed
        from glass.geo.gt.deldt    import del_rst

        # Send DEM to GRASS GIS
        grs_dem = rst_to_grs(dem, 'grs_dem', as_cmd=True)
    
        # Produce Viewshed for each point in obs
        for idx, row in obs.iterrows():
            # Get Viewshed raster
            vrst = grs_viewshed(
                grs_dem, (row.geometry.x, row.geometry.y),
                '{}_{}'.format(vis_basename, str(row[obs_id])),
                max_dist=maxdst, obs_elv=obselevation
            )
            
            # Export Raster to File
            frst = grs_to_rst(vrst, os.path.join(workspace, vrst + '.tif'))
            
            # Raster to Array
            img = gdal.Open(frst)
            num = img.ReadAsArray()
            
            # Two Dimension to One Dimension
            # Reshape Array
            numone = num.reshape(num.shape[0] * num.shape[1])
            
            # Get Indexes with visibility
            visnum = np.arange(numone.shape[0]).astype(np.uint32)
            visnum = visnum[numone == 1]
            
            # Get rows indexes
            visrow = visnum / num.shape[0]
            visrow = visrow.astype(np.uint32)
            
            # Get cols indexes
            viscol = visnum - (visrow * num.shape[1])
            
            # Visibility indexes to Pandas DataFrame
            idxnum = np.full(visrow.shape, row[obs_id])
            visdf = pd.DataFrame({
                'pntid' : idxnum, 'rowi' : visrow,
                'coli': viscol
            })
            
            # Pandas DF to database
            # Create Visibility table
            df_to_db(
                new_db, visdf, vis_basename,
                api='psql', colGeom=None,
                append=None if not idx else True
            )
            
            # Delete all variables
            numone = None
            visnum = None
            visrow = None
            viscol = None
            idxnum = None
            visdf = None
            del img
            
            # Delete GRASS GIS File
            del_rst(vrst)
            
            # Delete TIFF File
            del_file(frst)
            frst = None

    thrds = [mp.Process(
        target=run_viewshed_by_cpu, name='th-{}'.format(str(i+1)),
        args=(i+1, dbname, dfs[i], dem, epsg,
            'vistoburn', 10000, 200)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    return 1
