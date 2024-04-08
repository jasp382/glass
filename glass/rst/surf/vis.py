"""
Viewshed related tools
"""

import os
import multiprocessing as mp
import pandas          as pd
import numpy           as np

from glass.rd.shp   import shp_to_obj
from glass.pys.oss  import cpu_cores
from glass.pd.split import df_split
from glass.wenv.grs import grass_session


def viewshed(demrst, obsShp, output):
    """
    This tool computes a visibility analysis using observer points from
    a point shapefile.
    """
    
    from glass.pys     import execmd
    from glass.pys.oss import fprop
    from glass.it.rst  import saga_to_tif
    
    SAGA_RASTER = os.path.join(
        os.path.dirname(output),
        f"sg_{fprop(output, 'fn')}.sgrd"
    )
    
    cmd = (
       f"saga_cmd ta_lighting 6 -ELEVATION {demrst} -POINTS {obsShp} "
       f"-VISIBILITY {SAGA_RASTER} -METHOD 0"
    )
    
    outcmd = execmd(cmd)
    
    # Convert to Tiif
    saga_to_tif(SAGA_RASTER, output)
    
    return output


def thrd_viewshed(dem, pnt_obs, obs_id, out_folder,
                  maxdist=None, obselv=None, targelv=None, dirmin=None, dirmax=None):
    """
    Compute Viewshed for all points in pnt_obs using
    a multiprocessing approach
    """

    import geopandas as gp
    
    # Points to DataFrame
    if type(pnt_obs) != gp.GeoDataFrame:
        obs_df = shp_to_obj(pnt_obs)
    
    else:
        obs_df = pnt_obs

    # Split DF by the number of cores
    n_cpu = cpu_cores()
    dfs   = df_split(obs_df, n_cpu)

    def run_viewshed_by_cpu(tid, obs, dem, output, vis_basename='vis'):

        # Create GRASS GIS location
        loc_name = f'loc_{str(tid)}'
        gbase = grass_session(output, loc=loc_name, srs=dem)

        from glass.it.rst       import rst_to_grs, grs_to_rst
        from glass.rst.surf.grs import grs_viewshed

        # Send DEM to GRASS GIS
        grs_dem = rst_to_grs(dem, as_cmd=True)
    
        # Produce Viewshed for each point in obs
        for idx, row in obs.iterrows():

            if dirmin and dirmax:
                drange = (row[dirmin], row[dirmax])
            else:
                drange = None

            vrst = grs_viewshed(
                grs_dem, (row.geometry.x, row.geometry.y),
                f'{vis_basename}_{str(row[obs_id])}',
                max_dist=maxdist, obs_elv=obselv,
                targ_elv=targelv,
                dirange=drange
            )
        
            frst = grs_to_rst(vrst, os.path.join(output, vrst + '.tif'))

    thrds = [mp.Process(
        target=run_viewshed_by_cpu, name=f'th-{str(i+1)}',
        args=(
            i+1, dfs[i], dem, out_folder,
            'visto'
        )
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
    
    from osgeo          import gdal

    from glass.pys.oss  import mkdir
    from glass.prop.prj import shp_epsg
    from glass.wt.sql   import df_to_db
    from glass.pys.oss  import del_file
    from glass.sql.db   import create_pgdb
    from glass.pys.num  import get_minmax_fm_seq_values
    
    # Get Work EPSG
    epsg = shp_epsg(pnt_obs)
    
    # Points to DataFrame
    obs_df = shp_to_obj(pnt_obs)

    # Split DF by the number of cores
    n_cpu = cpu_cores()
    dfs   = df_split(obs_df, n_cpu)

    def run_viewshed_by_cpu(tid, db, obs, dem, srs,
        vis_basename='vis', maxdst=None, obselevation=None):
        # Create Database
        new_db = create_pgdb(f"{db}_{str(tid)}")
        
        # Points to Database
        pnt_tbl = df_to_db(
            new_db, obs, 'pnt_tbl', api='psql', 
            epsg=srs, geom_type='POINT', col_geom='geometry')

        # Create GRASS GIS Session
        workspace = mkdir(os.path.join(
            os.path.dirname(dem),
            f'work_{str(tid)}'
        ))
        loc_name = 'vis_loc'
        gbase = grass_session(workspace, loc=loc_name, srs=dem)

        from glass.it.rst   import rst_to_grs, grs_to_rst
        from glass.rst.surf import grs_viewshed
        from glass.wenv.grs import del_rst

        # Send DEM to GRASS GIS
        grs_dem = rst_to_grs(dem, 'grs_dem', as_cmd=True)
    
        # Produce Viewshed for each point in obs
        for idx, row in obs.iterrows():
            # Get Viewshed raster
            vrst = grs_viewshed(
                grs_dem, (row.geometry.x, row.geometry.y),
                f'{vis_basename}_{str(row[obs_id])}',
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

            # Get Indexes intervals
            visint = get_minmax_fm_seq_values(visnum)
            
            # Get rows indexes
            _visint = visint.reshape(visint.shape[0] * visint.shape[1])
            visrow = _visint / num.shape[1]
            visrow = visrow.astype(np.uint32)
            
            # Get cols indexes
            viscol = _visint - (visrow * num.shape[1])

            # Reshape
            visrow = visrow.reshape(visint.shape)
            viscol = viscol.reshape(visint.shape)

            # Split array
            irow, erow = np.vsplit(visrow.T, 1)[0]
            icol, ecol = np.vsplit(viscol.T, 1)[0]
            
            # Visibility indexes to Pandas DataFrame
            idxnum = np.full(irow.shape, row[obs_id])
            
            visdf = pd.DataFrame({
                'pntid' : idxnum, 'rowi' : irow, 'rowe' : erow,
                'coli': icol, 'cole' : ecol
            })
            
            # Pandas DF to database
            # Create Visibility table
            df_to_db(
                new_db, visdf, vis_basename,
                api='psql', col_geom=None,
                append=None if not idx else True
            )
            
            # Delete all variables
            numone  = None
            visnum  = None
            visint  = None
            _visint = None
            visrow  = None
            viscol  = None
            irow    = None
            erow    = None
            icol    = None
            ecol    = None
            idxnum  = None
            visdf   = None
            del img
            
            # Delete GRASS GIS File
            del_rst(vrst)
            
            # Delete TIFF File
            del_file(frst)
            frst = None

    thrds = [mp.Process(
        target=run_viewshed_by_cpu, name=f'th-{str(i+1)}',
        args=(i+1, dbname, dfs[i], dem, epsg,
            'vistoburn', 10000, 500)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    return 1



def visdb_to_rst(demrst, pntobs, obs_id, db, orst):
    """
    demrst = '/home/osmtolulc/mrgis/vistofire/cmb_dem10.tif'
    pntobs = '/home/osmtolulc/mrgis/vistofire/pnt_incendio.shp'
    obs_id = 'pnt_fid'
    """

    pnt_id = [1, 2]

    import numpy as np
    from osgeo import gdal

    from glass.sql.q  import q_to_obj
    from glass.it.rst import obj_to_rst

    # Get Raster Shape
    rsrc = gdal.Open(demrst, gdal.GA_ReadOnly)

    rows, cols = rsrc.RasterYSize, rsrc.RasterXSize

    # Get Array with cells with visibility == 1
    whr = " OR ".join([
        f"pntid = {str(p)}" for p in pnt_id
    ])

    q = (
        "SELECT idx FROM ("
            "SELECT generate_series("
                f"(rowi * {str(cols)}) + coli, "
                f"(rowe * {str(cols)}) + cole "
            ") AS idx "
            "FROM vistoburn "
            f"WHERE {whr}"
        ") AS foo "
        "GROUP BY idx "
        "ORDER BY idx"
    )

    visidx = q_to_obj(db, q, db_api='psql')

    allidx = np.arange(rows * cols).astype(np.uint32)
    visimg = np.zeros(rows * cols)

    np.place(visimg, np.isin(allidx, visidx.idx), 1)

    visimg = visimg.reshape((rows, cols))

    obj_to_rst(visimg,orst, rsrc, noData=0)

    return db

