"""
Visibility to LULC Classes of interest

Calculations for all country of Portugal
"""

import os
import pandas as pd
import multiprocessing as mp
from osgeo import ogr

from glass.rd.shp   import shp_to_obj
from glass.pd.split import df_split
from glass.gobj     import create_polygon
from glass.pys.oss  import lst_ff, mkdir, cpu_cores, del_folder
from glass.wenv.grs import run_grass
from glass.pys.web  import data_from_get, data_from_post, get_file
from glass.pys.zzip import unzip


# GLOBAL VARIABLES
API_MAIN_URL = 'http://172.16.3.31/api/geodb'
CREDENTIALS = ('kurosaki', 'zangetsu++0012')

CELL_DIM = 20000
EPSG     = 3763


def cell_work(cellid, geom, obs_dt, dem_dt, wfolder):
    """
    Produce visibility raster for one cell
    """

    # Create processing folder
    gw = mkdir(os.path.join(wfolder, 'visproc_' + str(cellid)))

    # Get Observation Points
    dataext = data_from_post(
        "{}/getdata/".format(API_MAIN_URL),
        postdata={
            "dataset" : obs_dt,
            "geom"    : geom,
            "epsg"    : EPSG
        }, credentials=CREDENTIALS
    )

    obs_pnt = get_file("{}/download/{}/".format(
        API_MAIN_URL, dataext['data']['token']
    ), os.path.join(gw, 'obspoints.zip'), useWget=True)

    unzip(obs_pnt, gw)
    obs_shp = lst_ff(gw, file_format='.shp')[0]

    # Expand cell area
    geom_env = ogr.CreateGeometryFromWkt(geom).GetEnvelope()

    geomexp = create_polygon([
        (geom_env[0] - CELL_DIM, geom_env[3] + CELL_DIM),
        (geom_env[1] + CELL_DIM, geom_env[3] + CELL_DIM),
        (geom_env[1] + CELL_DIM, geom_env[2] - CELL_DIM),
        (geom_env[0] - CELL_DIM, geom_env[2] - CELL_DIM),
        (geom_env[0] - CELL_DIM, geom_env[3] + CELL_DIM)
    ], api='ogr').ExportToWkt()

    # Get DEM
    dtext = data_from_post(
        "{}/getdata/".format(API_MAIN_URL),
        postdata={
            "dataset" : dem_dt,
            "geom"    : geomexp,
            "epsg"    : EPSG
        }, credentials=CREDENTIALS
    )

    dem = get_file("{}/download/{}/".format(
        API_MAIN_URL, dtext['data']['token']
    ), os.path.join(gw, 'dem.tif'), useWget=True)

    # Obs points to DataFrame
    obs_df = shp_to_obj(obs_shp)

    # Create GRASS GIS location
    loc = 'loc_' + str(cellid)

    gbase = run_grass(gw, location=loc, srs=dem)

    # Start GRASS GIS Session
    import grass.script.setup as gsetup
    gsetup.init(gbase, gw, loc, 'PERMANENT')

    from glass.it.rst import rst_to_grs, grs_to_rst
    from glass.g.rst.surf import grs_viewshed
    from glass.g.rst.alg  import rstcalc
    from glass.g.deldt         import del_rst

    grs_dem = rst_to_grs(dem, 'grs_dem', as_cmd=True)

    # Produce Viewshed for each obs point
    vl = []
    i = 1
    e = 1
    for idx, row in obs_df.iterrows():
        vrst = grs_viewshed(
            grs_dem, (row.geometry.x, row.geometry.y),
            "visrst_{}".format(str(idx)),
            max_dist=20000
        )
    
        vl.append(vrst)
    
        if i == 100:
            # Join Rasters into only one
            orst = rstcalc(" + ".join(vl), 'joinvis_' + str(e), api="grass")

            # Delete temporary raster
            del_rst(vl, ascmd=True)

            vl = [orst]
            i = 1
            e += 1
        
        else:
            i += 1
    
    # Produce final raster
    if len(vl) == 1:
        fvis = vl[0]
    else:
        fvis= rstcalc(" + ".join(vl), 'joinvis_f', api="grass")
    
    visrst = grs_to_rst(fvis, os.path.join(wfolder, 'visrst_{}.tif'.format(
        str(cellid)
    )))

    del_folder(gw)

    return visrst

def run_th(_df, wf, d_obs, d_dem):
    """
    Run Threads
    """

    for ix, r in _df.iterrows():
        cell_work(r.cellid, r.geom, d_obs, d_dem, wf)


if __name__ == '__main__':
    """
    Get Visibility Stuff
    """

    # Datasets
    obs_dataset = 'obs_fire_cos18'
    dem_dataset = 'eudem20_10'

    # Workfolder
    workfolder = '/home/jasp/mrgis/obs_fire_cos18_eudem'

    # Get Rerence GRID
    refgrid = pd.DataFrame(data_from_get(
        "{}/grid/".format(API_MAIN_URL),
        auth=CREDENTIALS
    ))

    # Remove cells when the data for that cell is already
    # created
    exres = pd.DataFrame(lst_ff(
        workfolder, file_format='.tif', rfilename=True
    ), columns=['filename'])

    if exres.shape[0]:
        exres['name']    = exres.filename.str.split('.', expand=True)[0]
        exres['format']  = exres.filename.str.split('.', expand=True)[1]
        exres['jcellid'] = exres.name.str.split('_', expand=True)[1].astype(int)

        refgrid = refgrid.merge(exres, how='left', left_on='cellid', right_on='jcellid')
        refgrid = refgrid[refgrid.cellid != refgrid.jcellid]
        refgrid.reset_index(inplace=True)
        refgrid.drop([
            'index', 'filename', 'name', 'format', 'jcellid'
        ], axis=1, inplace=True)

    # Split DF
    ncpu = cpu_cores() - 2
    dfs = df_split(refgrid, ncpu)

    # Run procedure
    ths = [mp.Process(
        target=run_th, name='th_' + str(o),
        args=(dfs[o], workfolder, obs_dataset, dem_dataset)
    ) for o in range(len(dfs))]

    for t in ths:
        t.start()
    
    for t in ths:
        t.join()

