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

    from glass.cons.stl import get_ibands, get_lwibands
    from glass.pys.oss  import lst_ff, fprop
    from glass.pys.tm   import now_as_str
    from glass.wenv.grs import run_grass
    from glass.rst.rcls import rcls_rules

    # Constants
    bands = [
        'b02', 'b03', 'b04', 'b05', 'b06', 'b07',
        'b08', 'b8a', 'b09', 'b11', 'b12'
    ]
    ibands, lwbands = get_ibands(), get_lwibands()

    _ibands = {ibands[i] : lwbands[i] for i in range(len(ibands))}

    # List Images
    tifs = lst_ff(img_folder, file_format=fformat)

    # ID tiles and days
    imgs = {}
    for img in tifs:
        name = fprop(img, 'fn')
    
        np = name.split('_')
        _b = f"{np[-2]}_{np[-1]}"
        _d = np[-3].split('T')[0]
    
        if _d not in imgs:
            imgs[_d] = {}
        
        imgs[_d][_ibands[_b]] = img
    
    # Create GRASS GIS Session
    ws, loc = ofolder, f"loc_{now_as_str()}"

    grsb = run_grass(ws, location=loc, srs=refimg)
    
    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, loc, 'PERMANENT')

    # GRASS GIS methods
    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.rst.rcls import rcls_rst
    from glass.rst.mos  import rsts_to_mosaic, rseries
    from glass.rst.alg  import grsrstcalc

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

    for img in imgs:
        # Import all bands
        for b in imgs[img]:
            if b == 'aot':
                continue
        
            imgs[img][b] = rst_to_grs(imgs[img][b], f'{b}_{img}')
    
        # Reclassify SCL
        rcls = rcls_rst(
            imgs[img]['scl'], scl_rules,
            f'dmask_{img}', api='grass'
        )
        _rs = grsrstcalc(rcls, f'dmaskcp_{img}')
    
        # Get only cells with data
        for b in bands:
            nb = grsrstcalc(
                f'{imgs[img][b]} + {_rs}',
                f'd_{imgs[img][b]}'
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
        ), is_int=True)
    
        for s in stats:
            orst = rseries(timeseries[b], f'{b}_{s}', stats[s],as_cmd=True)
            grs_to_rst(orst, os.path.join(
                ofolder, f'{bname}_{orst}.tif'
            ), is_int=True if s != 'avg' and s != 'ddev' else False)

    return ofolder

