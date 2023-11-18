"""
Resampling methods for Satellite images
"""

import os


def resample_s2img(imgzip, ref, ofolder, reflyr=None,
                   bands=['b02', 'b03', 'b04', 'b05', 'b06', 'b07', 'b08', 'b11', 'b12', 'scl']):
    """
    Unzip and resample the bands of a sentinel-2 image
    """

    from glass.cons.sat import bandsmap, get_lwibands
    from glass.dtt.stl  import unzip_img
    from glass.pys.oss  import fprop, mkdir
    from glass.pys.tm import now_as_str
    from glass.prop.ext import get_ext
    from glass.prop.prj import get_epsg
    from glass.wt.shp import coords_to_boundshp
    from glass.wenv.grs import run_grass

    bandsww = bands if bands else get_lwibands()

    bmap = bandsmap()

    # Check if outfolder exists
    if not os.path.exists(ofolder):
        mkdir(ofolder, overwrite=None)
    
    # Create Workspace
    ws = mkdir(os.path.join(ofolder, now_as_str(utc=True)))

    # Unzip Image
    _bands = unzip_img(imgzip, ws)

    # ref raster
    refrst = _bands["B02_10m"]
    img_epsg = get_epsg(refrst)
    
    # Get reference Shapefile
    left, right, bottom, top = get_ext(ref, oepsg=img_epsg, geolyr=reflyr)

    refshp = coords_to_boundshp(
        (left, top),
        (right, bottom), img_epsg,
        os.path.join(ws, 'refshp.shp')
    )

    # Get image date
    iname = fprop(imgzip, 'fn')
    idate = iname.split('_')[2]
    idate = idate.split('T')[0]

    # Start GRASS GIS Session
    grsb = run_grass(
        ws, grassBIN='grass78', location='resample',
        srs=refrst
    )

    import grass.script.setup as gsetup

    gsetup.init(grsb, ws, 'resample', 'PERMANENT')

    """
    Import packages related with GRASS GIS
    """
    from glass.it.rst    import rst_to_grs, grs_to_rst, grs_to_mask
    from glass.it.shp    import shp_to_grs
    from glass.wenv.grs  import shp_to_region, align_region, rst_to_region
    from glass.rst.rcls  import set_null
    from glass.dtt.torst import grsshp_to_grsrst as shp_to_rst

    # Import all bands we want
    bands_ = {bmap[b] : _bands[b] for b in _bands}
    gbands = [rst_to_grs(
        bands_[b], f'{b}_{idate}'
    ) for b in bands_ if b in bandsww]

    # Import Clip shape to GRASS GIS
    clip_shp = shp_to_grs(refshp, asCMD=True)

    # Set Clip Shape as region
    shp_to_region(clip_shp)

    # Align region
    align_region(gbands[0])

    # Clip Shape to Raster
    clip_rst = shp_to_rst(
        clip_shp, 1, f'rst_{clip_shp}',
        cmd=True
    )

    # Set Mask
    rst_to_region(clip_rst)
    grs_to_mask(clip_rst)

    # Export bands
    # Set 0 as NULL
    # Put 0 as NoData Value
    bands_lst = []

    for i in gbands:
        set_null(i, 0, ascmd=True)
        ob = grs_to_rst(
            i, os.path.join(ofolder, f'{i}.tif'),
            rtype=int, nodata=0
        )

        bands_lst.append(ob)

    return bands_lst


def resample_s2img_shp(shp, folder, ofolder, refgeo=None):
    """
    Resample all sentinel 2 images listed
    in a given Shapefile

    Create a folder for each month
    """

    import pandas as pd

    from glass.rd.shp  import shp_to_obj
    from glass.pys.tm  import now_as_str
    from glass.pys.oss import lst_ff, mkdir, del_folder
    from glass.dtt.stl import unzip_img
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
                    isint=True, clipgeo=refgeo,
                    ws=zfolder
                )
            
                # Remove temporary data
                del_folder(zfolder)

    return ofolder

