"""
Resampling methods for Satellite images
"""


def resample_s2img_shp(shp, folder, ofolder):
    """
    Resample all sentinel 2 images listed
    in a given Shapefile

    Create a folder for each month
    """

    import pandas as pd
    import os

    from glass.rd.shp  import shp_to_obj
    from glass.pys.tm  import now_as_str
    from glass.pys.oss import lst_ff, mkdir, del_folder
    from glass.dtr.stl import unzip_img
    from glass.rst.rmp import match_cellsize_and_clip

    # List images in folder
    imgs = lst_ff(folder, file_format='.zip')

    # Read shapefile with the images list
    img_df = shp_to_obj(shp)

    # Get months
    img_df['date']  = pd.to_datetime(img_df.beginposit)#, format='%Y%m%d%H%M%S')
    img_df['date']  = img_df.date.dt.floor('s')
    img_df['month'] = img_df.date.dt.month

    months = img_df.month.unique()
    months.sort()

    # Resample
    for m in months:
        imgs = img_df[img_df.month == m]
    
        if not imgs.shape[0]: continue
    
        mf = mkdir(os.path.join(ofolder, f"m_{str(m)}"))
    
        for i, r in imgs.iterrows():
            zfolder = mkdir(os.path.join(mf, now_as_str()), overwrite=True)
            _zip = os.path.join(folder, f"{r.title}.zip")
        
            if os.path.exists(_zip):
                # Unzip images
                bands = unzip_img(_zip, zfolder)
    
                # Match cellsize and clip
                bands = match_cellsize_and_clip(
                    [bands[b] for b in bands],
                    bands["B02_10m"], mf,
                    isint=True, clipgeo=None,
                    ws=zfolder
                )
            
                # Remove temporary data
                del_folder(zfolder)

    return ofolder

