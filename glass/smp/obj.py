"""
Sampling tools
"""

def fishnet(top_left, bottom_right, x, y, outfishnet=None, epsg=None, xy_row_col=None):
    """
    Produce fishnet from extent

    - Use pandas to do the job
    """
    
    from math import ceil
    import numpy as np
    import pandas as pd
    from shapely import wkt
    import geopandas as gp
    from glass.pd.dagg import dfcolstorows
    from glass.wt.shp   import df_to_shp
    
    x_min, y_max  = top_left
    x_max, y_min  = bottom_right
    
    if xy_row_col:
        # X, Y are row and col number
        # Find cellsize
        nrow = x
        ncol = y
        
        width  = ceil((x_max - x_min) / nrow)
        height = ceil((y_max - y_min) / ncol)
    
    else:
        # X, Y are cellsize
        # Find N Row and Col
        
        width  = x
        height = y
        nrow = ceil((y_max - y_min) / height)
        ncol = ceil((x_max - x_min) / width)
    
    # Create array with right shape
    num = np.full((nrow, ncol), 1, dtype=np.ubyte)
    
    # Array to DataFrame
    numdf = pd.DataFrame(num)
    numdf['idx'] = numdf.index
    
    fishtbl = dfcolstorows(numdf, 'col', 'val', colFid='idx')
    
    # Add polygon vertices
    fishtbl['x_min'] = x_min + (width * fishtbl.col)
    fishtbl['x_max'] = fishtbl.x_min + width
    fishtbl['y_max'] = y_max - (height * fishtbl.idx)
    fishtbl['y_min'] = fishtbl.y_max - height
    
    fishtbl['x_min'] = fishtbl.x_min.astype(str)
    fishtbl['x_max'] = fishtbl.x_max.astype(str)
    fishtbl['y_max'] = fishtbl.y_max.astype(str)
    fishtbl['y_min'] = fishtbl.y_min.astype(str)
    
    # Create Polygon WKT
    fishtbl['wkt'] = 'POLYGON ((' + fishtbl.x_min + ' ' + fishtbl.y_max + ', ' + \
        fishtbl.x_min + ' ' + fishtbl.y_min + ", " + \
        fishtbl.x_max + ' ' + fishtbl.y_min + ", " + \
        fishtbl.x_max + ' ' + fishtbl.y_max + ", " + \
        fishtbl.x_min + ' ' + fishtbl.y_max + '))'
    
    # Create Polygon from WKT
    fishtbl["geom"] = fishtbl.wkt.apply(wkt.loads)
    
    # Delete unecessary cols
    fishtbl.drop([
        "val", "idx", "col", "x_min", "x_max",
        "y_min", "y_max", "wkt"
    ], axis=1, inplace=True)
    
    # DataFrame to GeoDataFrame
    fishtbl = gp.GeoDataFrame(
        fishtbl, geometry="geom",
        crs=f'EPSG:{str(epsg)}' if epsg else None
    )
    
    if outfishnet:
        # GeoDataFrame to File
        return df_to_shp(fishtbl, outfishnet)
    else:
        return fishtbl

