"""
Download Sentinel Data
"""

import os

def lst_prod(shpext, start_time, end_time,
             outshp=None, platname="Sentinel-2", plevel="Level-2A",
             max_cloud_cover=None, s2_cellid=None):
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

    def get_grid_id(row):
        row['cellid'] = row.title.split('_')[5][1:]
    
        return row
    
    from sentinelsat    import SentinelAPI, geojson_to_wkt
    from glass.rd.shp   import shp_to_obj
    from glass.pys      import obj_to_lst
    from glass.pys.oss  import fprop
    from glass.wt.shp   import df_to_shp
    from glass.cons.stl import con_datahub
    from glass.prop     import check_isRaster
    from glass.gobj     import wkt_to_geom

    # Get global vars
    gvar = con_datahub()
    user, passw, url = gvar["USER"], gvar["PASSWORD"], gvar["URL"]
    
    # Get Search Area
    if os.path.isfile(shpext):
        if fprop(shpext, 'ff') == '.json':
            boundary = geojson_to_wkt(shpext)
    
        else:
            if check_isRaster(shpext):
                from glass.gp.ext import rstext_to_shp

                # Raster extent to shape
                shpext = rstext_to_shp(shpext, os.path.join(
                    os.path.dirname(shpext),
                    fprop(shpext, 'fn') + '.shp'
                ))
            
            boundary = shp_to_obj(
                shpext, output='array', fields=None,
                geom_as_wkt=True, srs_to=4326
            )[0]["GEOM"]
    else:
        # Assuming we have an WKT
        # Check if WKT  is valid
        tstgeom = wkt_to_geom(shpext)

        if not tstgeom:
            raise ValueError('Invalid geometry')
        
        boundary = shpext
    
    # Create API instance
    api = SentinelAPI(user, passw, url)
    
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
    df_prod = df_prod.apply(lambda x: get_grid_id(x), axis=1)

    if s2_cellid:
        s2_cellid = obj_to_lst(s2_cellid)

        # Filter
        df_prod = df_prod[df_prod.cellid.isin(s2_cellid)]        
    
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

    from glass.rd.shp import shp_to_obj
    from glass.pd    import merge_df
    from glass.wt.shp import df_to_shp
    from glass.it.pd  import df_to_geodf

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


def down_imgs(inTbl, imgIDcol, outFolder=None):
    """
    Download Images in Table
    """
    
    import os
    from sentinelsat   import SentinelAPI
    from glass.rd.shp import shp_to_obj
    from glass.cons.stl import con_datahub
    
    of = outFolder if outFolder else os.path.dirname(inTbl)
    
    # Tbl to df
    df_img = shp_to_obj(inTbl)
    
    # API Instance
    user, password = con_datahub()
    api = SentinelAPI(user, password, URL_COPERNICUS)
    
    # Download Images
    for idx, row in df_img.iterrows():
        # Check if file already exists
        outFile = os.path.join(outFolder, row.identifier + '.zip')
        
        if os.path.exists(outFile):
            print('IMG already exists')
            continue
        else:
            api.download(row[imgIDcol], directory_path=outFolder)

