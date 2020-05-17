"""
Network and Raster
"""


def cost_surface(dem, lulc, lulc_col, prod_lulc, roads, kph, barr, output):
    """
    Tool for make a cost surface based on the roads, slope, land use and
    physical barriers. ach cell has a value that represents the resistance to
    the movement.
    """
    
    import os
    from glass.pys.oss    import mkdir, fprop
    from glass.wenv.grs import run_grass
    from glass.prop.rst import get_cellsize, rst_distinct

    def lulc_weight(a, b):
        return {'a' : {'cls' : 'b'}}
    
    def get_slope_cat():
        return None
    
    """
    Auxiliar Methods
    """
    
    def combine_to_cost(rst_combined, lst_rst, work, slope_weight,
                        rdv_cos_weight, cellsize, mode_movement):
        # The tool r.report doesn't work properly, for that we need some aditional information
        l = []
        for i in lst_rst:
            FT_TF_GRASS(i, os.path.join(work, i + '.tif'), 'None')
            values = rst_distinct(os.path.join(work, i + '.tif'), gisApi='gdal')
            l.append(min(values))
        # ******
        # Now, we can procede normaly
        txt_file = os.path.join(work, 'text_combine.txt')
        raster_report(rst_combined, txt_file)
        open_txt = open(txt_file, 'r')
        c = 0
        dic_combine = {}
        for line in open_txt.readlines():
            try:
                if c == 4:
                    dic_combine[0] = [str(l[0]), str(l[1])]
                elif c >= 5:
                    pl = line.split('|')
                    cat = pl[2].split('; ')
                    cat1 = cat[0].split(' ')
                    cat2 = cat[1].split(' ')
                    dic_combine[int(pl[1])] = [cat1[1], cat2[1]]
                c += 1
            except:
                break
        
        cst_dic = {}
        for key in dic_combine.keys():
            cls_slope = int(dic_combine[key][0])
            cos_vias = int(dic_combine[key][1])
            if cos_vias >= 6:
                weight4slope = slope_weight[cls_slope]['rdv']
                if mode_movement == 'pedestrian':
                    weight4other = (3600.0 * cellsize) / (5.0 * 1000.0)
                else:
                    weight4other = (3600.0 * cellsize) / (cos_vias * 1000.0)
            else:
                weight4slope = slope_weight[cls_slope]['cos']
                weight4other = rdv_cos_weight[cos_vias]['weight']
            cst_dic[key] = (weight4slope * weight4other) * 10000000.0
        return cst_dic
    
    def Rules4CstSurface(dic, work):
        txt = open(os.path.join(work, 'cst_surface.txt'), 'w')
        for key in dic.keys():
            txt.write(
                '{cat}  = {cst}\n'.format(cat=str(key), cst=str(dic[key]))
            )
        txt.close()
        return os.path.join(work, 'cst_surface.txt')
    
    """
    Prepare GRASS GIS Environment
    """

    ws = os.path.dirname(output)
    loc = f'loc_{fprop(output, "fn")}'

    # Start GRASS GIS Engine
    gb = run_grass(ws, location=loc, srs=dem)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')
    
    # Import GRASS GIS Modules
    from glass.it.shp    import grs_to_shp, shp_to_grs
    from glass.rst.surf  import slope
    from glass.rst.rcls  import interval_rules
    from glass.rst.rcls  import category_rules
    from glass.tbl.col   import add_fields, cols_calc
    from glass.gp.ovl    import grsunion
    from glass.it.rst    import rst_to_grs, grs_to_rst
    from glass.rst.local import combine
    from glass.rst.alg   import rstcalc
    from glass.prop.rst  import raster_report
    from glass.rst.mos   import rsts_to_mosaic
    from glass.dp.torst  import shp_to_rst
    from glass.rst.rcls  import rcls_rst, set_null
    
    """Global variables"""
    # Workspace for temporary files
    tmp = mkdir(os.path.join(ws, loc, 'tmp'), overwrite=True)
    
    # Cellsize
    cellsize = float(get_cellsize(dem), gisApi='gdal')

    # Land Use Land Cover weights
    lulcref = lulc_weight(prod_lulc, cellsize)
    # Slope classes and weights
    slope_cls = get_slope_cat()
    
    """Make Cost Surface"""
    # Generate slope raster
    grsdem = rst_to_grs(dem, fprop(dem, 'fn'))
    gslope = slope(grsdem, 'dclv', api="pygrass")
    
    # Reclassify Slope
    rulesdclv = interval_rules(slope_cls, os.path.join(tmp, 'slope.txt'))
    rslope = rcls_rst(gslope, rulesdclv, 'rcls_dclv', api="pygrass")
    
    # LULC - Dissolve, union with barriers and conversion to raster
    grslulc = shp_to_grs(lulc, fprop(lulc, 'fn'))

    add_fields(grslulc, {'leg' : 'INT'}, api="pygrass")

    for k in lulcref:
        l = lulcref[k]['cls']

        sql = " OR ".join([f"{lulc_col}='{i}'" for i in l])

        cols_calc(grslulc, 'leg', int(k), sql, ascmd=True)

    grsbar = shp_to_grs(barr, fprop(barr, 'fn'))

    barrcos = grsunion(grslulc, grsbar, 'barrcos', cmd=True)

    cols_calc(barrcos, 'a_leg', 99, 'b_cat=1')

    rstbarrcols = shp_to_rst(
        barrcos, 'a_leg', None, None, 'rst_barrcos',
        api='pygrass'
    )
    
    # Reclassify this raster - convert the values 99 to NULL or NODATA
    set_null(rstbarrcols, 99, ascmd=True)
    
    # Add the roads layer to the GRASS GIS
    rdv = shp_to_grs(roads, fprop(roads, 'fn'))

    if kph == 'pedestrian':
        add_fields(rdv, {'foot': 'INT'}, api="pygrass")
        cols_calc(rdv, 'foot', 50, 'foot IS NULL')
        rrdv = shp_to_rst(rdv, 'foot', None, None, f'rst_{rdv}', api='pygrass')
    else:
        rrdv = shp_to_rst(rdv, kph, None, None, f'rst_{rdv}', api='pygrass')
    
    # Merge LULC/BARR and Roads
    mos = rsts_to_mosaic(rrdv, rstbarrcols, 'rdv_barrcos')
    
    # Combine LULC/BARR/ROADS with Slope
    cmb = combine(rslope, mos, 'rst_combine', api="pygrass")
    
    """
    Estimating cost for every combination at rst_combine
    The order of the rasters on the following list has to be the same of
    GRASS Combine"""
    cst = combine_to_cost(
        cmb, [rslope, mos],
        tmp, slope_cls, lulc_weight, cellsize,
        kph if kph != 'pedestrian' else 'foot'
    )
    
    # Reclassify combined rst
    rulessurf = category_rules(cst, os.path.join(tmp, 'r_surface.txt'))
    rcls_rst('rst_combine', rulessurf, 'cst_tmp', api='pygrass')

    rstcalc('cst_tmp / 10000000.0', 'cst_surface', api='pygrass')
    grs_to_rst('cst_surface', output)

    return output


def acumulated_cost(cst_surface, dest_pnt, cst_dist):
    """
    Uses a cost surface to estimate the time between each cell and the 
    close destination
    """
    
    from glass.rst.alg import rstcalc
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
    rstcalc('cst_dist / 60.0', 'CstDistMin', api="grass")
    # Export result
    grs_to_rst('CstDistMin', cst_dist)
    
    return cst_dist

