"""
Satellite image fusion
"""

import os

from glass.pys.oss      import lst_ff, fprop, mkdir
from glass.pys.tm       import now_as_str
from glass.wenv.grs     import grass_session
from glass.dtt.stl      import unzip_img
from glass.cons.sat     import get_lwibands
from glass.it.rst       import rst_to_grs, grs_to_rst
from glass.rst.mos      import rseries 
from glass.rst.rcls.grs import set_null, rcls_rules, grs_rcls
from glass.rst.alg      import grsrstcalc
from glass.it.cubes     import gtifs_to_cube



def month_representative(img_folder, refimg, ofolder, bname, fformat='.tif'):
    """
    Get a representatives bands for one month

    The bands of all images for a month should be in the 
    same folder
    """

    # List Images
    tifs = lst_ff(img_folder, file_format=fformat)

    # ID tiles and days
    imgs = {}
    for img in tifs:
        name = fprop(img, 'fn')
    
        _b, _d = name.split('_')
    
        if _d not in imgs:
            imgs[_d] = {}
        
        imgs[_d][_b] = img
    
    # Create GRASS GIS Session
    ws, loc = ofolder, f"loc_{now_as_str()}"

    grsb = grass_session(ws, loc=loc, srs=refimg)

    # GRASS GIS methods
    from glass.rst.mos import rsts_to_mosaic

    # For each image
    # Get only cells with data
    timeseries = {}

    scl_rules = rcls_rules({
        0  : 'NULL', 1 : 0,
        2  : 0, 3 : 0,
        4  : 0, 5 : 0, 6 : 0, 7 : 0,
        8  : 'NULL', 9 : 'NULL',
        10 : 'NULL',
        11 : 0
    }, os.path.join(ws, loc, 'only_data.txt'))

    for day in imgs:
        # Import all bands
        for b in imgs[day]:
            imgs[day][b] = rst_to_grs(imgs[day][b])
    
        # Reclassify SCL
        rcls = grs_rcls(
            imgs[day]['scl'], scl_rules,
            f'dmask_{day}', as_cmd=True
        )
        _rs = grsrstcalc(rcls, f'dmaskcp_{day}')
    
        # Get only cells with data
        for b in imgs[day]:
            if b == 'scl':
                continue

            nb = grsrstcalc(
                f'{imgs[day][b]} + {_rs}',
                f'd_{imgs[day][b]}'
            )
        
            if b not in timeseries:
                timeseries[b] = [nb]
        
            else:
                timeseries[b].append(nb)
    
    # Export representative images
    stats = {
        'avg' : 'average', 'mode' : 'mode',
        'min' : 'minimum', 'max' : 'maximum',
        'ddev' : 'stddev'
    }

    for b in timeseries:
        patch_i = rsts_to_mosaic(timeseries[b], f'{b}_patch', api="grass")
    
        grs_to_rst(patch_i, os.path.join(
            ofolder, f'{bname}_{patch_i}.tif'
        ), as_cmd=True, dtype="UInt16", nodata=0)

        series_i = rseries(timeseries[b], f'{b}_median', 'median', as_cmd=True)

        grs_to_rst(series_i, os.path.join(
            ofolder, f'{bname}_{series_i}.tif'
        ), as_cmd=True, dtype="UInt16", nodata=0)
    
        #for s in stats:
            #orst = rseries(timeseries[b], f'{b}_{s}', stats[s],as_cmd=True)
            #grs_to_rst(orst, os.path.join(
                #ofolder, f'{bname}_{orst}.tif'
            #), rtype=int if s != 'avg' and s != 'ddev' else float)

    return ofolder



def month_median(months_folder, refrst, ofolder, fformat='.tif'):
    """
    Get representatives bands for each month in folder
    the representative value for each band is the median

    The bands of all images for a month should be in the 
    same folder
    """

    from glass.pys.oss import lst_fld

    # Create GRASS GIS Session
    ws, loc = ofolder, now_as_str(utc=True)

    gb = grass_session(ws, loc=loc, srs=refrst)

    # GRASS GIS Methods
    from glass.it.rst  import rst_to_grs, grs_to_rst
    from glass.rst.mos import rseries

    # List folders of each month
    mfolders = lst_fld(months_folder)

    # for each folder, list images
    # Get median for each month
    results = {}
    for mfld in mfolders:
        # List images
        imgs = lst_ff(mfld, file_format=fformat)

        # Organize images by band
        ibyband = {}
        for img in imgs:
            # Add image to GRASS GIS
            gimg = rst_to_grs(img)

            band = gimg.split('_')[0]

            if band not in ibyband:
                ibyband[band] = [gimg]
            
            else:
                ibyband[band].append(gimg)
        
        # For each band, get median
        # Export result
        month_k = os.path.basename(mfld)
        results[month_k] = []
        for band in ibyband:
            bmonth = rseries(
                ibyband[band], f'{band}_{month_k}',
                'median', as_cmd=True
            )

            _bmonth = grs_to_rst(
                bmonth,
                os.path.join(ofolder, f'{bmonth}.tif'),
                as_cmd=True, dtype='UInt16',
                nodata=0
            )

            results[month_k].append(_bmonth)

    return results


def month_processing(month_folder, out, outcube=None, bname=None,
                     bands=None, norm=None, chunks=(512, 512), ws=None):
    """
    Unzip, resample and calcule representative bands considering
    all images in a folder

    The script assumes that the images in the folder are
    from the same tile
    """
    
    bandsww = bands if bands else get_lwibands()

    if not os.path.exists(out):
        mkdir(out)

    if "SCL" not in bandsww:
        bandsww.append("SCL")
    
    if not ws and not outcube:
        ws = out
        
    elif not ws and outcube:
        ws = mkdir(os.path.dirname(out), timerand=True)
    
    if not os.path.exists(ws):
        mkdir(ws)

    loc = f'loc_{now_as_str(utc=True)}'

    # List Images and unzip them
    if isinstance(month_folder, str) and os.path.isdir(month_folder):
        izips = lst_ff(month_folder, file_format='.zip')
    
    else:
        izips = month_folder

    imgs = [unzip_img(
        img, ws if outcube else os.path.join(ws, f'img{loc}'), 
        bands=bandsww
    ) for img in izips]

    # Get Ref Raster
    refrst = imgs[0][bandsww[0]]

    # Create GRASS GIS Session
    gb = grass_session(ws, loc=loc, srs=refrst)

    # SCL reclassification rules
    scl_rules = rcls_rules({
        0  : 'NULL', 1 : 0,
        2  : 0, 3 : 0,
        4  : 0, 5 : 0, 6 : 0, 7 : 0,
        8  : 'NULL', 9 : 'NULL',
        10 : 'NULL',
        11 : 0
    }, os.path.join(ws, loc, 'scl_reclass.txt'))

    # Import bands into GRASS GIS
    # _imgs = {
    #    "b02" : ["band_02_img1", "band_02_img2", ...],
    #    "b03" : ["band_03_img1", "band_03_img2", ...],
    #    ...
    #}
    _imgs = {}
    for img in imgs:
        # Process SCL
        gscl = rst_to_grs(img["SCL"])

        rscl = grs_rcls(
            gscl, scl_rules,
            f'cmask_{gscl}', as_cmd=True
        )
        _rscl = grsrstcalc(rscl, f'cmaskcp_{gscl}')

        for band in img:
            if band == 'SCL': continue

            gband = rst_to_grs(img[band])

            set_null(gband, 0, ascmd=True)

            # Remove clouds
            _gband = grsrstcalc(f'{gband} + {_rscl}', f"masked_{gband}")

            if band not in _imgs:
                _imgs[band] = [_gband]
            
            else:
                _imgs[band].append(_gband)
    
    # Retrieve median
    bmedian = {}
    for b in _imgs:
        bm = rseries(_imgs[b], f'{b}_median', 'median', as_cmd=True)

        _dtype = 'UInt16'

        if norm:
            bm = grsrstcalc(
                f"{bm} / 10000.0",
                f'{b}_norm'
            )

            _dtype = 'Float64'

        # Export
        efolder = ws if outcube else out
        fname = f'{bm}.tif' if not bname else f'{bname}_{bm}.tif'
        bmedian[b] = grs_to_rst(
            bm,
            os.path.join(efolder, fname),
            as_cmd=True, dtype=_dtype,
            nodata=0 if _dtype=='UInt16' else -1
        )
    
    if outcube:
        # Export data to a cube
        cubebands, featnames = [], []
        for k in bandsww:
            cubebands.append(bmedian[k])
            featnames.append(k)
    
        gtifs_to_cube(cubebands, out, chunksize=chunks, featname=featnames)

        return outcube
    
    else:
        return bmedian

