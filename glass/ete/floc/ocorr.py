"""
Methods to support Occurrences Identification
"""


def ctb_to_intersect(ngrp):
    """
    Find which contributions must be intersected

    ** inputs **

    ngrp: dict = {
        id_contribution : [ids of all contributions intersecting the key one]
    }

    example

    ngrp = {
        1 : [2, 3, 4, 5],
        2 : [3, 6, 7, 8],
        3 : [8],
        4 : [],
        5 : [],
        6 : [7, 8],
        7 : [8]
    }

    will return the following groups:
    result = [
        [1, 2, 3],
        [1, 4],
        [1, 5],
        [2, 6, 7, 8],
        [3, 8]
    ]
    """

    grp = []

    # List all keys in ngrp
    ks = list(ngrp.copy().keys())

    # Create contribution groups
    for k in ks:
        while k in ngrp:
            if not ngrp[k]:
                del ngrp[k]
                continue
            
            # Each key | value pair is a group
            _grp = [k, ngrp[k][0]]
            remain = []

            i = 1
            while i < len(ngrp[k]):
                isg = None
                for e in ngrp[k][:i]:
                    if ngrp[k][i] in ngrp[e]:
                        isg = True
                
                    else:
                        isg = None
                
                        if not isg: break
                
                if isg:
                    _grp.append(ngrp[k][i])

                    for e in ngrp[k][:i]:
                        ngrp[e].remove(ngrp[k][i])
                    
                    i += 1
                
                else:
                    remain.append(ngrp[k][i])
                    ngrp[k].remove(ngrp[k][i])

            ngrp[k] = remain

            grp.append(_grp)
    
    return grp


def ctbs_to_obslocal(ctbs, output, tmax=30*60,
    datehour="datehour", ctbrst="ctbrst", rtbl=None):
    """
    Find Interest Locals by intersecting contributions
    """

    import datetime as dt
    import pandas as pd
    import os

    from glass.pys.oss  import fprop
    from glass.wenv.grs import run_grass
    from glass.prop.rst import rst_ext
    from glass.wt.rst   import ext_to_rst

    ws = os.path.dirname(output)
    oname = fprop(output, 'fn')

    loc = f'loc_{oname}'

    now = dt.datetime(2023, 1, 5, 0, 0, 0)
    nowunix = int((now - dt.datetime(1970, 1, 1)).total_seconds())

    cdf = pd.DataFrame(ctbs)

    # Datehour to datetime
    cdf["datehour"] = pd.to_datetime(
        cdf[datehour], format='%Y-%m-%d %H:%M:%S')

    # Get unix timestamp 
    cdf["unix"] = cdf.datehour - dt.datetime(1970, 1, 1)
    cdf["unix"] = cdf.unix.dt.total_seconds()
    cdf["unix"] = cdf.unix.astype(int)

    # Get time difference
    cdf["tcont"] = nowunix - cdf.unix

    cdf["difp"] = cdf.tcont / tmax

    cdf["weight"] = 0.5 * cdf["difp"] * cdf["difp"] * cdf["difp"] - \
        1.5 * cdf["difp"] *cdf["difp"] + 1
    
    if rtbl:
        from glass.wt import obj_to_tbl

        obj_to_tbl(cdf, rtbl)
    
    # Create reference raster
    rexts = pd.DataFrame(
        [rst_ext(r[ctbrst]) for i, r in cdf.iterrows()],
        columns=["left", "right", "bottom", "top"]
    )

    left, top = rexts.left.min(), rexts.top.max()
    right, bottom = rexts.right.max(), rexts.bottom.min()

    ref = ext_to_rst(
        (left, top), (right, bottom),
        os.path.join(ws, f'ref_{oname}.tif'),
        cellsize=10, epsg=3763
    )

    # Start GRASS GIS Session
    gb = run_grass(ws, location=loc, srs=ref)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    from glass.it.rst  import rst_to_grs, grs_to_rst
    from glass.rst.alg import grsrstcalc

    # Import rasters
    grsts = [rst_to_grs(
        r[ctbrst], fprop(r.ctbrst, 'fn')
    ) for i, r in cdf.iterrows()]

    # Intersect Rasters
    exp = " + ".join([
        f"({grsts[i]} * {str(r.weight)})" 
    for i, r in cdf.iterrows()])

    res = grsrstcalc(exp, oname)

    # Export result
    grs_to_rst(res, output, dtype="Float32", nodata=0)

    return output


def firelocs_fusion(lst):
    """
    Agregate arrays with firelocs if two arrays
    have a commum object

    Transform this:
    lst = [
        [180, 182, 190],
        [181, 190],
        [186, 185],
        [182, 183, 184],
        [200, 201, 202],
        [202, 207, 209],
        [209, 210, 211],
        [211, 212]
    ]

    Into this:
    lst = [
        [180, 181, 182, 183, 184, 190],
        [186, 185],
        [200, 201, 202, 207, 209, 210, 211, 212]
    ]
    """

    import numpy as np

    i = 0
    e = 1
    ni = None
    ll = len(lst)
    while i < ll - 1:
        #print(f"{str(i)} | {str(e)}")
        #print(len(lst))
    
        l, _l = lst[i], lst[e]
    
        for o in l:
            if o in _l:
                l.extend(_l)
            
                ni = True
                break
    
        if ni:
            lst[i] = list(np.unique(l))
        
            lst.remove(_l)
        
            ll = len(lst)
        
            ni = None
            continue
    
        else:
            if e == len(lst) -1:
                i += 1
                e = i + 1
            else:
                e += 1
    
    return lst

