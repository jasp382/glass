"""
Satellite image fusion
"""

import os


def month_representative(img_folder, refimg, ofolder, bname, fformat='.tif'):
    """
    Get a representatives bands for one month

    The bands of all images for a month should be in the 
    same folder
    """

    from glass.pys.oss  import lst_ff, fprop
    from glass.pys.tm   import now_as_str
    from glass.wenv.grs import run_grass
    from glass.rst.rcls.grs import rcls_rules, grs_rcls

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

    grsb = run_grass(ws, location=loc, srs=refimg)
    
    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, loc, 'PERMANENT')

    # GRASS GIS methods
    from glass.it.rst  import rst_to_grs, grs_to_rst
    from glass.rst.mos import rsts_to_mosaic, rseries
    from glass.rst.alg import grsrstcalc

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
        ), as_cmd=True, rtype=int, dtype="UInt16", nodata=0)

        series_i = rseries(timeseries[b], f'{b}_median', 'median', as_cmd=True)

        grs_to_rst(series_i, os.path.join(
            ofolder, f'{bname}_{series_i}.tif'
        ), as_cmd=True, rtype=int, dtype="UInt16", nodata=0)
    
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

    from glass.pys.oss import lst_ff, lst_fld, fprop
    from glass.pys.tm   import now_as_str
    from glass.wenv.grs import run_grass

    # Create GRASS GIS Session
    ws, loc = ofolder, now_as_str(utc=True)

    gb = run_grass(ws, location=loc, srs=refrst)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

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
                as_cmd=True, rtype=int, dtype='UInt16',
                nodata=0
            )

            results[month_k].append(_bmonth)

    return results

