"""
Download Sentinel Data
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from sentinelsat    import SentinelAPI, geojson_to_wkt
from glass.cons.sat import con_datahub
from glass.pys      import obj_to_lst
from glass.pys.oss  import mkdir
from glass.pys.web  import get_file
from glass.rd.shp   import shp_to_obj

from glass.acq.stl.apis import TokenManager


def lst_prod(shpext, start_time, end_time,
             outshp=None, platname="Sentinel-2", plevel="Level-2A",
             max_cloud_cover=None, s2_tileid=None):
    """
    List Sentinel Products for one specific area
    
    platformname:
    * Sentinel-1
    * Sentinel-2
    * Sentinel-3

    processinglevel:
    * Level-1A
    * Level-1B
    * Level-1C
    * Level-2A
    ...
    """
    
    from glass.pys     import obj_to_lst
    from glass.pys.oss import fprop
    from glass.wt.shp  import df_to_shp
    from glass.gobj    import wkt_to_geom
    from glass.gp.cnv  import ext_to_polygon

    def get_tileid(row):
        row['tileid'] = row.title.split('_')[5][1:]
    
        return row

    # Get global vars
    gvar = con_datahub()
    user, passw, url = gvar["USER"], gvar["PASSWORD"], gvar["URL"]
    
    # Get Search Area
    if os.path.isfile(shpext):
        if fprop(shpext, 'ff') == '.json':
            boundary = geojson_to_wkt(shpext)
    
        else:
            boundary = ext_to_polygon(
                shpext, out_srs=4326,
                outaswkt=None
            )
    else:
        # Check if we have a geodatabase
        if '.gdb' in shpext:
            lyr = os.path.basename(shpext)

            gdb = os.path.dirname(shpext)

            if gdb[-4:] != '.gdb':
                gdb = os.path.dirname(gdb)
            
            boundary = ext_to_polygon(
                gdb, out_srs=4326,
                outaswkt=None, geolyr=lyr
            )
        
        else:
            # Assuming we have an WKT
            # Check if WKT  is valid
            tstgeom = wkt_to_geom(shpext)

            if not tstgeom:
                raise ValueError('Invalid geometry')
        
            boundary = shpext
    
    # Create API instance
    api = SentinelAPI(user, passw)
    
    # Search for products
    products = api.query(
        boundary, date=(start_time, end_time),
        platformname=platname,
        cloudcoverpercentage=(
            0,
            100 if not max_cloud_cover else max_cloud_cover
        ),
        processinglevel=plevel
    )
    
    df_prod = api.to_geodataframe(products)

    if not df_prod.shape[0]:
        return df_prod
    
    cols = df_prod.columns.values

    if 'ingestiondate' in cols:
        df_prod['ingestiondate'] = df_prod.ingestiondate.astype(str)
    
    if 'beginposition' in cols:
        df_prod['beginposition'] = df_prod.beginposition.astype(str)
    
    if 'endposition' in cols:
        df_prod['endposition']   = df_prod.endposition.astype(str)
    
    if 'generationdate' in cols:
        df_prod['generationdate']= df_prod.generationdate.astype(str)
    
    df_prod.reset_index(inplace=True)
    df_prod.drop(['index'], axis=1, inplace=True)

    # ID Cell ID
    df_prod = df_prod.apply(lambda x: get_tileid(x), axis=1)

    if s2_tileid:
        s2_tileid = obj_to_lst(s2_tileid)

        # Filter
        df_prod = df_prod[df_prod.tileid.isin(s2_tileid)]        
    
    # Export results to Shapefile
    if outshp:
        return df_to_shp(df_prod, outshp)
    else:
        return df_prod


def lst_prod_by_cell_and_year(shp, id_col, year, outshp,
    platform="Sentinel-2", processingl='Level-2A', epsg=32629):
    """
    Get a list of images:
    * one for each grid in shp;
    * one for each month in one year - the choosen image will be the one
    with lesser area occupied by clouds;
    total_images = grid_number * number_months_year
    """

    from glass.rd.shp     import shp_to_obj
    from glass.dtt.mge.pd import merge_df
    from glass.wt.shp     import df_to_shp
    from glass.it.pd      import df_to_geodf

    months = {
        '01' : '31', '02' : '28', '03' : '31',
        '04' : '30', '05' : '31', '06' : '30',
        '07' : '31', '08' : '31', '09' : '30',
        '10' : '31', '11' : '30', '12' : '31'
    }

    # Open SHP
    grid = shp_to_obj(shp, srs_to=4326)

    def get_grid_id(row):
        row['cellid'] = row.title.split('_')[5][1:]
    
        return row
    
    # Search for images
    dfs = []
    for idx, cell in grid.iterrows():
        for k in months:
            start = f"{str(year)}{k}01"
            end   = f"{str(year)}{k}{months[k]}"

            if year == 2018 and processingl == 'Level-2A':
                if k == '01' or k == '02':
                    plevel = 'Level-2Ap'
                else:
                    plevel = processingl
            else:
                plevel = processingl
        
        prod = lst_prod(
            cell.geometry.wkt, start, end,
            platname=platform, procLevel=plevel
        )

        if not prod.shape[0]:
            continue

        # Get area
        prod = prod.to_crs(f'EPSG:{str(epsg)}')
        prod['areav'] = prod.geometry.area / 1000000

        # We want only images with more than 70% of data
        prod = prod[prod.areav >= 7000]

        # ID Cell ID
        prod = prod.apply(lambda x: get_grid_id(x), axis=1)
        # Filter Cell ID
        prod = prod[prod.cellid == cell[id_col]]

        # Sort by cloud cover and date
        prod = prod.sort_values([
            'cloudcoverpercentage', 'ingestiondate'
        ], ascending=[True, True])

        # Get only the image with less cloud cover
        prod = prod.head(1)

        dfs.append(prod)
    
    fdf = merge_df(dfs)
    fdf = df_to_geodf(fdf, 'geometry', epsg)

    df_to_shp(fdf, outshp)

    return outshp


def lst_prod_bytile(stime, etime, tiles, platname="Sentinel-2", procLevel="Level-2A",
    max_cloud_cover=None):
    """
    List Sentinel Products for one specific sentinel tile
    
    platformname:
    * Sentinel-1
    * Sentinel-2
    * Sentinel-3

    processinglevel:
    * Level-1A
    * Level-1B
    * Level-1C
    * Level-2A
    ...
    """

    gvar = con_datahub()
    user, passw, url = gvar["USER"], gvar["PASSWORD"], gvar["URL"]

    tiles = obj_to_lst(tiles)

    # Create API instance
    api = SentinelAPI(user, passw, url)

    # Query
    p = []
    for t in tiles:
        pp = api.query(
            date = (stime, etime),
            platformname=platname,
            cloudcoverpercentage=(
                0,
                100 if not max_cloud_cover else max_cloud_cover
            ),
            processinglevel=procLevel,
            tileid=t
        )

        dfp = api.to_geodataframe(pp)

        p.append(dfp)
    
    return p



#################################################################
#################################################################



def download_sentinel_products(imglist:str, img_id:str, downcol:str, outfolder:str, MAX_WORKERS:int=4) -> str:
    """
    Download Sentinel Products from Copernicus Data Ecosystem

    Download all products listed in imglist to outfolder
    """

    # Open imglist file
    imgdf = shp_to_obj(imglist)

    # Create column with tile id
    imgdf['tile'] = imgdf[img_id].str.split('_').str[-2]

    # Get Token
    token_mgr = TokenManager()
    token_mgr.get_token()

    # Create output folder if not exists
    if not os.path.exists(outfolder):
        mkdir(outfolder)
    
    def download_scene(row):
        tilefolder = os.path.join(outfolder, row["tile"])

        if not os.path.exists(tilefolder):
            mkdir(tilefolder)
    
        scene_id = row[img_id]
        url = row[downcol]

        out = os.path.join(tilefolder, f"{scene_id}.zip")

        token = token_mgr.get_token()

        imgzip = get_file(url, out, useWget=True, quiet=True, token=token)

        if not imgzip:
            return scene_id, "Error"
        else:
            return scene_id, "Sucesso"

    # DOwnload images with multiprocessing
    results = []

    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_scene, row, token_mgr): idx
            for idx, row in imgdf.iterrows()
        }

        for fut in as_completed(futures):
            scene_id, status = fut.result()

            print(f"[{scene_id}] {status}")
            results.append((scene_id, status))

        elapsed = time.time() - start
        print(f"Downloads concluídos em {elapsed/60:.1f} min")

    token_mgr.close()

    return outfolder

