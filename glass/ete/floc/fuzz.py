"""
Fuzzy methods to detect fire locations
"""


import numpy as np
import os

from glass.wt.rst import obj_to_rst


def ctb_errors_specs(cdf, topleft, cellsize, dmax, epsg,
    dc=None, usergeom="usergeom",
    ugaz="ugazimute", gaz="gazimute", geom="geomc", direction="direction",
    directbf="directbf", dshadow="dsun", ctbshp=None):
    """
    Return Contributions errors:
    * Erro na direccao do sol;
    * Erro na direccao do incendio;
    * Erro na direccao.

    And contribution raster specs
    """

    from glass.it.pd  import obj_to_geodf
    from glass.wt.shp import df_to_shp

    # Get Reference raster properties
    left, top = topleft
    cellx, celly = cellsize

    # Drop unecessary columns from the contributions dataframe
    if dc:
        _dc = [c for c in dc if c in cdf.columns.values]

        cdf.drop(_dc, axis=1, inplace=True)
    
    # Get azimute for each contribution
    cdf["isusgeom"]  = ~cdf[usergeom].isna()
    cdf["isdbf"]     = ~cdf[directbf].isna()
    cdf["isdshadow"] = ~cdf[dshadow].isna()

    cdf["azimute"] = np.where(cdf.isusgeom, cdf[ugaz], cdf[gaz])

    # Get Reference Position
    cdf["geom"] = np.where(cdf.isusgeom, cdf[usergeom], cdf[geom])

    cdf = obj_to_geodf(cdf, 'geom', epsg)

    cdf["x"] = cdf.geom.x
    cdf["y"] = cdf.geom.y

    # Get contribution raster geometric properties
    cdf['ps_top']  = cdf.y + dmax
    cdf['ps_left'] = cdf.x - dmax

    # Get contribution indexes in the Reference Rster
    cdf["colidx"] = (cdf.ps_left - left) / abs(cellx)
    cdf["colidx"] = cdf.colidx.astype(int)

    cdf["rowidx"] = (top - cdf.ps_top) / abs(celly)
    cdf["rowidx"] = cdf.rowidx.astype(int)

    # Get True origin for each contribution raster
    cdf["top"] = top - (cdf.rowidx * abs(celly))
    cdf["left"] = left + (cdf.colidx * abs(celly))

    # Erro na direcao do fogo
    # Quando sao dadas duas direcoes para o fogo, o erro 
    # e igual ao modulo da diferença entre estas direcoes 
    # (quando nao e dada a 2 direcao, nao existe erro associado 
    # - o campo fica vazio)
    cdf["dfire_error"] = cdf[direction] - cdf[directbf]
    
    cdf["dfire_error"] = np.where(
        cdf.isdbf, cdf.dfire_error.abs(), np.NaN
    )

    # Direcao do sol medido
    cdf["dsun_measured"] = np.where(
        cdf.isdshadow, np.where(
            cdf[dshadow] - 180 >= 0,
            cdf[dshadow] - 180, cdf[dshadow] + 180
        ), np.NaN
    )

    # Erro na direccao do Sol
    # = sol-AzimuteSol 
    # quando maior que 180 é considerado o angulo complementar até 360
    cdf["errodirectsun"] = cdf.azimute - cdf.dsun_measured
    cdf["errodirectsun"] = cdf.errodirectsun.astype(float)

    cdf["errodirectsun"] = np.where(
        cdf.isdshadow,
        cdf.errodirectsun.round(decimals=0), np.NaN
    )
    
    cdf["errodirectsun"] = np.where(
        cdf.errodirectsun > 180,
        360 - cdf.errodirectsun, cdf.errodirectsun
    )

    cdf["errodirectsun"] = np.where(
        cdf.errodirectsun < -180,
        360 + cdf.errodirectsun, cdf.errodirectsun
    )

    # Erro na direcao
    # soma de erros
    cdf["errodirection"] = cdf["errodirectsun"]

    
    '''
    cdf["errodirection"] = np.where(
        (cdf.isdbf) & (cdf.isdshadow),
        cdf.errodirectsun/cdf.errodirectsun.abs() * (cdf.errodirectsun.abs() + cdf.dfire_error), 
        np.NaN
    ) 

    cdf["errodirection"] = np.where(
        (cdf.isdbf) & (~cdf.isdshadow),
        cdf.dfire_error, cdf.errodirection
    )

    cdf["errodirection"] = np.where(
        (~cdf.isdbf) & (cdf.isdshadow),
        cdf.errodirectsun, cdf.errodirection
    )

    cdf["errodirection"] = np.where(
        cdf.errodirection > 180, 180, cdf.errodirection
    )

    '''
    cdf["iserrodir"] = ~cdf.errodirection.isna()


    # Export Contributions Shapefile
    if ctbshp:
        df_to_shp(cdf, ctbshp)
    
    return cdf


def fx_rst(topleft, shape, cellsize, pnt, errod, direction, dmax, fxrst, epsg):
    """
    Produce Raster with the possibility of a fire be
    in a strip with a certain direction interval
    """

    import pandas as pd

    from glass.it.pd    import pnt_dfwxy_to_geodf
    from glass.pys.oss  import fprop, copy_file
    from glass.pys.tm   import now_as_str
    from glass.wenv.grs import run_grass
    from glass.wt.rst   import rst_from_origin
    from glass.wt.shp   import df_to_shp

    # Geo Params
    left, top    = topleft
    nrows, ncols = shape
    cellx, celly = cellsize
    pnt_x, pnt_y = pnt

    # Setup work environment
    ws, loc = os.path.dirname(fxrst), f"fx_{now_as_str()}"

    # Create Reference Raster
    refrst = rst_from_origin(
        (left, top), (nrows, ncols),
        (cellx, celly),
        os.path.join(ws, 'refrst.tif'), epsg
    )

    # Start GRASS GIS Session
    gb = run_grass(ws, grassBIN='grass78', location=loc, srs=refrst)

    import grass.script.setup as gsetup
    gsetup.init(gb, ws, loc, 'PERMANENT')

    # Move ref raster
    refrst = copy_file(refrst, os.path.join(ws, loc, 'refrst.tif'), move=True)

    # Import GRASS GIS modules
    from glass.it.rst     import grs_to_rst
    from glass.it.shp     import shp_to_grs
    from glass.dtt.torst  import grsshp_to_grsrst
    from glass.rst.alg    import grsrstcalc
    from glass.rst.direct import grs_bearing_from_pnt
    from glass.rst.dst    import grow_distance
    from glass.rst.rcls.grs import set_null

    # Get bearing raster
    bearing = grs_bearing_from_pnt(pnt, "bearingrst", asint=None)

    # Get Distance raster
    # Distance from each cell and point
    pntdf = pd.DataFrame(
        [[1, pnt_x, pnt_y]],
        columns=['pid', 'x', 'y']
    )
    pntdf = pnt_dfwxy_to_geodf(pntdf, 'x', 'y', epsg)

    pntshp = df_to_shp(pntdf, os.path.join(ws, loc, 'pntshp.shp'))

    pntgrs = shp_to_grs(pntshp, 'pntgrs', asCMD=True)

    pntrst = grsshp_to_grsrst(pntgrs, 'pid', 'pntrst', cmd=True)

    rdist = grow_distance(pntrst, 'distrst', api="grass")

    # Fuzzy Trapezio
    if errod == 0:
        errod = 1
    elif errod >= 0:
        direction = direction + errod / 2.0
    else:
        direction = direction + errod / 2.0

        errod=-errod

    m = 2.0 / errod
    b = 2.0 * direction / errod

    dmin   = direction - errod
    dmin0  = direction - errod / 2.0
    
    _dmax  = direction + errod
    _dmax0 = direction + errod / 2.0

    sumrst = []
    if dmin <= 0:
        if dmin0 <= 0:
            exp1 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} - 360 >= {str(dmin)} && "
                f"{bearing} - 360 < {str(dmin0)}, "
                f"{str(m)} * ({bearing} - 360) - {str(b)} + 2.0, 0.0"
            ")")
        
            exp2 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} - 360 >= {str(dmin0)} && "
                f"{bearing} - 360 <= 0, 1.0, 0.0"
            ")")
        
            exp3 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} > 0 && "
                f"{bearing} <= {str(_dmax0)}, 1.0, 0.0"
            ")")
        
            exp4 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} > {str(_dmax0)} && "
                f"{bearing} <= {str(_dmax)}, "
                f"-{str(m)} * {bearing} + {str(b)} + 2.0, 0.0"
            ")")
    
        else:
            exp1 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} - 360 >= {str(dmin)} && "
                f"{bearing} - 360 < 0, "
                f"{str(m)} * ({bearing} - 360) - {str(b)} + 2.0, 0.0"
            ")")
        
            exp2 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} >= 0 && {bearing} < {str(dmin0)}, "
                f"{str(m)} * {bearing} - {str(b)} + 2.0, 0.0"
            ")")
        
            exp3 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} >= {str(dmin0)} && "
                f"{bearing} <= {str(_dmax0)}, 1.0, 0.0"
            ")")
        
            exp4 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} > {str(_dmax0)} && "
                f"{bearing} <= {str(_dmax)}, "
                f"-{str(m)} * {bearing} + {str(b)} + 2.0, 0.0"
            ")")
    
        sumrst.extend([exp1, exp2, exp3, exp4])

    elif _dmax > 360:
        if _dmax0 > 360:
            exp1 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} >= {str(dmin)} && "
                f"{bearing} < {str(dmin0)}, "
                f"{str(m)} * {bearing} - {str(b)} + 2.0, 0.0"
            ")")
        
            exp2 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} >= {str(dmin0)} && "
                f"{bearing} <= 360, 1.0, 0.0"
            ")")
        
            exp3 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} + 360 > 360 && "
                f"{bearing} + 360 <= {str(_dmax0)}, 1.0, 0.0"
            ")")
        
            exp4 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} + 360 > {str(_dmax0)} && "
                f"{bearing} + 360 <= {str(_dmax)}, "
                f"-{str(m)} * ({bearing} + 360) + {str(b)} + 2.0, 0.0"
            ")")
        else:
            exp1 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} >= {str(dmin)} && "
                f"{bearing} < {str(dmin0)}, "
                f"{str(m)} * {bearing} - {str(b)} + 2.0, 0.0"
            ")")
        
            exp2 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} >= {str(dmin0)} && "
                f"{bearing} <= {str(_dmax0)}, 1.0, 0.0"
            ")")
        
            exp3 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} > {str(_dmax0)} && "
                f"{bearing} <= 360, "
                f"-{str(m)} * {bearing} + {str(b)} + 2.0, 0.0"
            ")")
        
            exp4 = ("if("
                f"{rdist} <= {str(dmax)} && "
                f"{bearing} + 360 > 360 && "
                f"{bearing} + 360 <= {str(_dmax)}, "
                f"-{str(m)} * ({bearing} + 360) + {str(b)} + 2.0, 0.0"
            ")")
    
        sumrst.extend([exp1, exp2, exp3, exp4])

    else:
        exp1 = ("if("
            f"{rdist} <= {str(dmax)} && "
            f"{bearing} >= {str(dmin)} && "
            f"{bearing} < {str(dmin0)}, "
            f"{str(m)} * {bearing} - {str(b)} + 2.0, 0.0"
        ")")
    
        exp2 = ("if("
            f"{rdist} <= {str(dmax)} && "
            f"{bearing} >= {str(dmin0)} && "
            f"{bearing} <= {str(_dmax0)}, 1.0, 0.0"
        ")")
    
        exp3 = ("if("
            f"{rdist} <= {str(dmax)} && "
            f"{bearing} > {str(_dmax0)} && "
            f"{bearing} <= {str(_dmax)}, "
            f"-{str(m)} * {bearing} + {str(b)} + 2.0, 0.0"
        ")")
    
        sumrst.extend([exp1, exp2, exp3])

    sumrst = [grsrstcalc(
        sumrst[e], f"rst_{str(e+1)}", ascmd=True
    ) for e in range(len(sumrst))]

    _fxrst = grsrstcalc(" + ".join(sumrst), fprop(fxrst, 'fn'), ascmd=True)

    set_null(_fxrst, 0, ascmd=True)

    grs_to_rst(_fxrst, fxrst, rtype=float, dtype="Float32", nodata=0)

    return fxrst


def np_fxrst(topleft, shape, cellsize, pnt, errod, direction, dmax, fxrst, epsg):
    """
    Produce Raster with the possibility of a fire be
    in a strip with a certain direction interval

    Numpy does the job
    """

    from glass.rst.direct import bearing_from_pnt
    from glass.rst.dst    import dist_from_pnt

    # Geo Params
    left, top    = topleft
    cellx, celly = cellsize

    # Get Bearing matrix
    bearing = bearing_from_pnt(
        topleft, shape, cellsize, pnt, resint=False
    )

    invbea = bearing - 360
    plusbea = bearing + 360

    # Get Distance raster
    # Distance from each cell and point
    dist = dist_from_pnt(topleft, shape, cellsize, pnt)
    
    # Fuzzy Trapezio
    if errod == 0:
        errod = 1
    elif errod >= 0:
        direction = direction + errod / 2.0
    else:
        direction = direction + errod / 2.0
        errod=-errod
        
    m = 2.0 / errod
    b = 2.0 * direction / errod

    dmin   = direction - errod
    dmin0  = direction - errod / 2.0
    
    _dmax  = direction + errod
    _dmax0 = direction + errod / 2.0

    if dmin <= 0:
        if dmin0 <= 0:
            a = np.where(
                (dist <= dmax) & (invbea >= dmin) & (invbea < dmin0),
                m * invbea - b + 2.0, 0.0
            )

            b_ = np.where(
                (dist <= dmax) & (invbea >= dmin0) & (invbea <= 0),
                1.0, 0.0
            )

            c = np.where(
                (dist <= dmax) & (bearing > 0) & (bearing <= _dmax0),
                1.0, 0.0
            )

            d = np.where(
                (dist <= dmax) & (bearing > _dmax0) & (bearing <= _dmax),
                -m * bearing + b + 2.0, 0.0
            )
        
        else:
            a = np.where(
                (dist <= dmax) & (invbea >= dmin) & (invbea < 0),
                m * invbea - b + 2.0, 0.0
            )

            b_ = np.where(
                (dist <= dmax) & (bearing >= 0) & (bearing < dmin0),
                m * bearing - b + 2.0, 0.0
            )

            c = np.where(
                (dist <= dmax) & (bearing >= dmin0) & (bearing <= _dmax0),
                1.0, 0.0
            )

            d = np.where(
                (dist <= dmax) & (bearing > _dmax0) & (bearing <= _dmax),
                -m * bearing + b + 2.0, 0.0
            )

        fx = a + b_ + c + d
    
    elif _dmax > 360:
        if _dmax0 > 360:
            a = np.where(
                (dist <= dmax) & (bearing >= dmin) & (bearing < dmin0),
                m * bearing - b + 2.0, 0.0
            )

            b_ = np.where(
                (dist <= dmax) & (bearing > dmin0) & (bearing <= 360),
                1.0, 0.0
            )

            c = np.where(
                (dist <= dmax) & (plusbea > 360) & (plusbea <= _dmax0),
                1.0, 0.0
            )

            d = np.where(
                (dist <= dmax) & (plusbea > _dmax0) & (plusbea <= _dmax),
                -m * plusbea + b + 2.0, 0.0
            )
        
        else:
            a = np.where(
                (dist <= dmax) & (bearing >= dmin) & (bearing < dmin0),
                m * bearing - b + 2.0, 0.0
            )

            b_ = np.where(
                (dist <= dmax) & (bearing >= dmin0) & (bearing <= _dmax0),
                1.0, 0.0
            )

            c = np.where(
                (dist <= dmax) & (bearing > _dmax0) & (bearing <= 360),
                -m * bearing + b + 2.0, 0.0
            )

            d = np.where(
                (dist <= dmax) & (plusbea > 360) & (plusbea <= _dmax),
                -m * plusbea + b + 2.0, 0.0
            )
        
        fx = a + b_ + c + d
    
    else: 
        a = np.where(
            (dist <= dmax) & (bearing >= dmin) & (bearing < dmin0),
            m * bearing - b + 2.0, 0.0
        )

        b_ = np.where(
            (dist <= dmax) & (bearing >= dmin0) & (bearing <= _dmax0),
            1.0, 0.0
        )

        c = np.where(
            (dist <= dmax) & (bearing > _dmax0) & (bearing <= _dmax),
            -m * bearing + b + 2.0, 0.0
        )

        fx = a + b_ + c
    
    # Export to raster
    gtrans = (left, cellx, 0, top, 0, celly)

    fx = fx.astype('float32')

    np.place(fx, fx < 0.1, 2)

    obj_to_rst(fx, fxrst, gtrans, epsg, noData=2) 
    return fxrst


def fx_to_geom(rst, reduce_raster=None):
    """
    ID Strip and convert it to vetorial geometry

    If reduce_raster, a new raster will be created
    with values only in the minimum bounding box considering
    cells with values
    """

    from glass.pys.oss  import fprop
    from glass.pys.tm   import now_as_str
    from glass.wenv.grs import run_grass
    from glass.rd.shp   import shp_to_obj
    from glass.prop.rst import get_cellsize

    # Setup work environment
    ws, loc = os.path.dirname(rst), f"fxgeom_{now_as_str()}"

    # Start GRASS GIS Session
    gb = run_grass(ws, grassBIN='grass78', location=loc, srs=rst)

    import grass.script.setup as gsetup
    gsetup.init(gb, ws, loc, 'PERMANENT')

    # Import GRASS GIS modules
    from glass.it.rst        import rst_to_grs, grs_to_mask, grs_to_rst
    from glass.it.shp        import grs_to_shp
    from glass.rst.rcls.grs  import grs_rcls, rcls_rules
    from glass.dtt.rst.toshp import rst_to_polyg
    from glass.wenv.grs      import shp_to_region

    # Import Strip raster
    fx = rst_to_grs(rst, fprop(rst, 'fn'), as_cmd=True)

    # Reclassify
    rules = rcls_rules({(0, 1000) : 1}, os.path.join(
        ws, loc, f'rules_{fx}.txt'
    ))

    fx_rcls = grs_rcls(fx, rules, f'rlcs_{fx}', as_cmd=True)

    # Raster to Vector
    fx_shp = rst_to_polyg(fx_rcls, f'shp_{fx}', api='grass')

    # Export vetor to ESRI Shapefile
    shp = grs_to_shp(fx_shp, os.path.join(
        ws, loc, f"{fx_shp}.shp"
    ), 'area')

    # Read Geometry and return it as WKT
    lst_geom = shp_to_obj(
        shp,
        srs_to=3763, output='array',
        geom_as_wkt=True
    )
    
    geom = lst_geom[0]["geometry"]

    if reduce_raster:
        # Set new region
        cx, cy = get_cellsize(rst)

        shp_to_region(fx_shp, cx)

        # Set Mask
        grs_to_mask(fx_rcls)

        grs_to_rst(
            fx, reduce_raster,
            rtype=float, dtype="Float32", nodata=0
        )

        return geom, reduce_raster

    return geom

