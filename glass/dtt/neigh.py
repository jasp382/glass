"""
Analise de vizinhanca
"""

def slope_neighbor(dem_folder, neightable, cellid, neighbor, outfolder):
    """
    Join file with neighbor files
    """

    import os

    from glass.pys.oss import lst_ff, fprop
    from glass.rd      import tbl_to_obj
    from glass.rst.mos import rsts_to_mosaic

    dems = lst_ff(dem_folder, file_format='.tif')

    neigh_df = tbl_to_obj(neightable)

    for dem in dems:
        demfullname = fprop(dem, 'fn')
        demnamelst = demfullname.split('_')
        demname = "_".join(demnamelst[:-1])
        # Get cell_id from raster file
        cid = int(demnamelst[-1])
        # Get neighbors rasters
        fneigh = neigh_df[neigh_df[cellid] == cid]
        vizinhos = fneigh[neighbor].tolist()
    
        rsts_viz = [os.path.join(
            dem_folder, f"{demname}_{str(v)}.tif"
        ) for v in vizinhos]
    
        # Get mosaic
        mos = rsts_to_mosaic([dem] + rsts_viz, os.path.join(
            outfolder, demfullname + '.tif'
        ), api='rasterio')
    
    return outfolder

