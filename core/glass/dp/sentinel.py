"""
Download Sentinel Data
"""

URL_COPERNICUS = 'https://scihub.copernicus.eu/dhus'

def lst_prod(shpExtent, start_time, end_time,
             outShp=None, platname="Sentinel-2", procLevel="Level-2A",
             max_cloud_cover=None):
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
    
    import os
    from sentinelsat   import SentinelAPI, read_geojson, geojson_to_wkt
    from datetime      import date
    from glass.dct.geo.fmshp import shp_to_obj
    from glass.pys.oss  import fprop
    from glass.dct.geo.toshp import df_to_shp
    from glass.cons.sentinel import con_datahub
    
    # Get Search Area
    if os.path.isfile(shpExtent):
        if fprop(shpExtent, 'ff') == '.json':
            boundary = geojson_to_wkt(shpExtent)
    
        else:
            boundary = shp_to_obj(
                shpExtent, output='array', fields=None,
                geom_as_wkt=True, srs_to=4326
            )[0]["GEOM"]
    else:
        # Assuming we have an WKT
        boundary = shpExtent
    
    # Create API instance
    user, password = con_datahub()
    api = SentinelAPI(user, password, URL_COPERNICUS)
    
    # Search for products
    products = api.query(
        boundary, date=(start_time, end_time),
        platformname=platname,
        cloudcoverpercentage=(0, 100 if not max_cloud_cover else max_cloud_cover),
        processinglevel=procLevel
    )
    
    df_prod = api.to_geodataframe(products)

    if not df_prod.shape[0]:
        return df_prod
    
    df_prod['ingestiondate'] = df_prod.ingestiondate.astype(str)
    df_prod['beginposition'] = df_prod.beginposition.astype(str)
    df_prod['endposition']   = df_prod.endposition.astype(str)
    
    # Export results to Shapefile
    if outShp:
        return df_to_shp(df_prod, outShp)
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

    from glass.dct.geo.fmshp import shp_to_obj
    from glass.dp.pd         import merge_df
    from glass.dct.geo.toshp import df_to_shp
    from glass.geo.obj.pd    import df_to_geodf

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
            start = "{}{}01".format(str(year), k)
            end   = "{}{}{}".format(str(year), k, months[k])

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
        prod = prod.to_crs('EPSG:{}'.format(str(epsg)))
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
    from sentinelsat   import SentinelAPI, read_geojson, geojson_to_wkt
    from glass.dct.geo.fmshp import shp_to_obj
    from glass.cons.sentinel import con_datahub
    
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

