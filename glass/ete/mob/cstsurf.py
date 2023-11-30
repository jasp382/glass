"""
Network and Raster
"""


def acumulated_cost(cst_surface, dest_pnt, cst_dist):
    """
    Uses a cost surface to estimate the time between each cell and the 
    close destination
    """
    
    from glass.rst.alg import grsrstcalc
    from glass.rst.dst import rcost
    from glass.it.rst  import rst_to_grs, grs_to_rst
    from glass.it.shp  import shp_to_grs
    
    # Add Cost Surface to GRASS GIS
    rst_to_grs(cst_surface, 'cst_surf')
    # Add Destination To GRASS
    shp_to_grs(dest_pnt, 'destination')
    # Execute r.cost
    rcost('cst_surf', 'destination', 'cst_dist')
    # Convert to minutes
    grsrstcalc('cst_dist / 60.0', 'CstDistMin')
    # Export result
    grs_to_rst('CstDistMin', cst_dist)
    
    return cst_dist


def mk_costsuf(dem, lulc, lucol, rdv, kph, barr, out):
    """
    Tool for make a cost surface based on the roads, slope, land use and
    physical barriers. each cell has a value that represents the resistance to
    the movement.
    """

    import os

    from glass.pys.oss  import mkdir, fprop
    from glass.wenv.grs import run_grass
    from glass.prop.rst import rst_cellsize

    _slope_rules = {
        (0, 10)      : 1,
        (10, 30)     : 1.5,
        (30, 50)     : 2,
        (50, 70)     : 3,
        (70, 100)    : 4,
        (100, 10000) : 5
    }
    slope_w = {
        1 : {'rdv' : 1, 'lu' : 1},
        2 : {'rdv' : 1.5, 'lu' : 1},
        3 : {'rdv' : 2, 'lu' : 1.5},
        4 : {'rdv' : 3, 'lu' : 1.5},
        5 : {'rdv' : 4, 'lu' : 2},
        6 : {'rdv' : 5, 'lu' : 2}
    }

    slope_rules = {
        (0, 10)      : 1,
        (10, 30)     : 2,
        (30, 50)     : 3,
        (50, 70)     : 4,
        (70, 100)    : 5,
        (100, 10000) : 6
    }

    lu_w = {
        1 : 18, 2 : 15, 3: 23, 4: 9, 5: 12
    }

    # Get cellsize
    csize = rst_cellsize(dem)

    # Setup GRASS GIS env
    ws, loc = mkdir(os.path.join(
        os.path.dirname(out), f"cstsuff_{fprop(out, 'fn')}"
    ), overwrite=True), f'loc_rstsuf'

    gb = run_grass(ws, location=loc, srs=dem)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    # Import GRASS GIS Modules
    from glass.it.shp     import shp_to_grs
    from glass.it.rst     import rst_to_grs, grs_to_rst
    from glass.rst.surf.grs import slope
    from glass.rst.rcls.grs import interval_rules, grs_rcls, category_rules
    from glass.gp.ovl.grs import grsunion
    from glass.gp.gen     import dissolve
    from glass.tbl.grs    import add_table, cols_calc
    from glass.tbl.col    import add_fields
    from glass.dtt.torst  import grsshp_to_grsrst
    from glass.rst.rcls.grs import set_null
    from glass.rst.mos    import rsts_to_mosaic
    from glass.rst.local  import combine
    from glass.prop.rst   import raster_report
    from glass.rst.alg    import grsrstcalc

    # Generate slope raster
    grsdem = rst_to_grs(dem, fprop(dem, 'fn'))
    rslope = slope(grsdem, 'dclv', data='percent', api='grass')

    # Reclassify slope
    dclvrules = interval_rules(slope_rules, os.path.join(
        ws, 'sloperules.txt'
    ))
    rcls_slope = grs_rcls(rslope, dclvrules, 'rcls_dclv', as_cmd=True)

    # LULC - Dissolve, union with barriers and conversion to raster
    glulc = shp_to_grs(lulc, fprop(lulc, 'fn'))
    gbarr = shp_to_grs(barr, fprop(barr, 'fn'))

    dlulc = dissolve(glulc, 'lulc_diss', lucol, api='grass')
    add_table(dlulc, None, lyrN=1, asCMD=True)

    barrlulc = grsunion(dlulc, gbarr, 'barrlu', cmd=True)

    cols_calc(barrlulc, 'a_cat', 99, 'b_cat is not null')

    rst_blu = grsshp_to_grsrst(
        barrlulc, 'a_cat', 'rst_blu',
        cmd=True
    )

    # Reclassify BARR-LULC raster
    set_null(rst_blu, 99, ascmd=True)

    # Add roads
    grdv = shp_to_grs(rdv, fprop(rdv, 'fn'))

    if kph == 'pedestrian':
        add_fields(grdv, {'foot' : 'INT'}, api='pygrass')
        cols_calc(grdv, 'foot', 50, 'foot IS NULL')

        kph = 'foot'

    rrdv = grsshp_to_grsrst(grdv, kph, f'rst_{grdv}', cmd=True)

    # Merge LULC/BARR and Roads
    mos = rsts_to_mosaic([rrdv, rst_blu], 'rdv_blu', api="grass")

    # Combine LULC/BARR/ROADS with Slope
    cmbrsts = [rcls_slope, mos]
    cmb = combine(cmbrsts, 'rst_combine', api="pygrass")

    """
    Estimating cost for every combination at rst_combine
    The order of the rasters on the following list has to be the same of
    GRASS Combine
    """
    rsttxt = raster_report(cmb, os.path.join(ws, 'cmb_report.txt'))

    # Get min slope value and min BARR/COS/RDV
    #minval = []
    #for r in cmbrsts:
        #tifr = grs_to_rst(r, os.path.join(ws, f"{r}.tif"), as_cmd=True)
        #rv = rst_distinct(tifr)

        #minval.append(min(rv))
    
    # Open Combine report and setup costs
    otxt = open(rsttxt, 'r')

    dcmb = {}
    c = 0
    for l in otxt.readlines():
        try:
            if c >= 4:
                pl = l.split('|')
                cat = pl[2].split('; ')
                cat1 = cat[0].split(' ')
                cat2 = cat[1].split(' ')

                dcmb[int(pl[1])] = [int(cat1[1]), int(cat2[1])]
            
            c += 1

        except: break
    
    # Get costs
    dcost = {}
    for k in dcmb:
        cslp, lurdv = dcmb[k]

        if not cslp or not lurdv:
            continue

        if lurdv >= 10:
            sw = slope_w[cslp]['rdv']
            
            vel = 5 if kph == 'foot' else lurdv
            wother = (3600.0 * csize) / (vel * 1000.0)
        
        else:
            sw = slope_w[cslp]['lu']
            wother = lu_w[lurdv]
        
        dcost[k] = round((sw * wother) * 10000000.0, 0)
    
    # Reclassify combine raster
    frules = category_rules(dcost, os.path.join(ws, 'tsurface.txt'))
    pfinal = rcls_rst(cmb, frules, 'rcls_cmb', api="pygrass")

    res = grsrstcalc(f'{pfinal} / 10000000.0', fprop(out, 'fn'))

    grs_to_rst(res, out, as_cmd=True)

    return out

