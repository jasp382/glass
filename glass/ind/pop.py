"""
Produce indicators
"""

import pandas as pd


def pop_within_area(mapunits, mapunits_id, outcol, subunits,
    subunits_id, pop_col, mapunits_fk,
    area_shp, output, res_areas=None, res_areas_fk=None):
    """
    Used to calculate % pop exposta a ruidos
    superiores a 65db
    Useful to calculate population a menos de x minutos de um tipo
    de equipamento

    Retuns population % living inside some polygons
    """

    import os
    from glass.rd.shp        import shp_to_obj
    from glass.dtr.ext.torst import shpext_to_rst
    from glass.wt.shp        import obj_to_shp
    from glass.pys.oss       import mkdir, fprop
    from glass.gp.ovl        import grsintersection
    from glass.prop.prj      import get_epsg
    from glass.wenv.grs      import run_grass

    # Prepare GRASS GIS Workspace configuration
    oname = fprop(output, 'fn')
    gw = mkdir(os.path.join(
        os.path.dirname(output), 'ww_' + oname
    ), overwrite=True)

    # Boundary to Raster
    w_epsg = get_epsg(area_shp)
    ref_rst = shpext_to_rst(
        mapunits, os.path.join(gw, 'extent.tif'),
        cellsize=10, epsg=w_epsg
    )

    # Create GRASS GIS Session
    loc = 'loc_' + oname
    gbase = run_grass(gw, location=loc, srs=ref_rst)

    import grass.script.setup as gsetup

    gsetup.init(gbase, gw, loc, 'PERMANENT')

    from glass.it.shp import shp_to_grs, grs_to_shp

    # Send data to GRASS GIS
    inres = res_areas if res_areas and res_areas_fk else subunits
    grs_res = shp_to_grs(inres, fprop(inres, 'fn'), asCMD=True)
    grs_ash = shp_to_grs(area_shp, fprop(area_shp, 'fn'), asCMD=True)

    # Run intersection
    int_ = grsintersection(
        grs_res, grs_ash, f'i_{grs_res}_{grs_ash}',
        cmd=True
    )

    # Export result
    res_int = grs_to_shp(int_, os.path.join(
        gw, int_ + '.shp'
    ), 'area')

    # Compute new indicator
    mapunits_df = shp_to_obj(mapunits)
    subunits_df = shp_to_obj(subunits)
    if res_areas and res_areas_fk:
        resareas_df = shp_to_obj(res_areas)
    int______df = shp_to_obj(res_int)

    # For each bgri, get hab area with population
    if res_areas and res_areas_fk:
        resareas_df['gtarea'] = resareas_df.geometry.area

        # Group By
        respop = pd.DataFrame({
            'areav' : resareas_df.groupby([res_areas_fk])['gtarea'].agg('sum')
        }).reset_index()

        # Join with subunits df
        respop.rename(columns={res_areas_fk: 'jtblfid'}, inplace=True)
        subunits_df = subunits_df.merge(
            respop, how='left',
            left_on=subunits_id, right_on='jtblfid'
        )
        subunits_df.drop(['jtblfid'], axis=1, inplace=True)
    else:
        subunits_df['areav'] = subunits_df.geometry.area

    # For each subunit, get area intersecting area_shp
    int______df['gtarea'] = int______df.geometry.area

    int_id = 'a_' + res_areas_fk if res_areas and res_areas_fk else \
        'a_' + subunits_id
    area_int = pd.DataFrame({
        'areai' : int______df.groupby([int_id])['gtarea'].agg('sum')
    }).reset_index()

    # Join with main subunits df
    area_int.rename(columns={int_id : 'jtblfid'}, inplace=True)

    subunits_df = subunits_df.merge(
        area_int, how='left', left_on=subunits_id,
        right_on='jtblfid'
    )
    subunits_df.drop(['jtblfid'], axis=1, inplace=True)

    subunits_df.areai = subunits_df.areai.fillna(0)
    subunits_df.areav = subunits_df.areav.fillna(0)

    subunits_df['pop_af'] = (subunits_df.areai * subunits_df[pop_col]) / subunits_df.areav

    subunits_pop = pd.DataFrame(subunits_df.groupby([mapunits_fk]).agg({
        pop_col : 'sum', 'pop_af' : 'sum'
    }))
    subunits_pop.reset_index(inplace=True)

    # Produce final table - mapunits table with new indicator
    subunits_pop.rename(columns={mapunits_fk: 'jtblid'}, inplace=True)

    mapunits_df = mapunits_df.merge(
        subunits_pop, how='left', left_on=mapunits_id, right_on='jtblid'
    )
    mapunits_df[outcol] = (mapunits_df.pop_af * 100) / mapunits_df[pop_col]

    mapunits_df.drop(['jtblid', pop_col, 'pop_af'], axis=1, inplace=True)

    obj_to_shp(mapunits_df, 'geometry', w_epsg, output)

    return output


def calc_iwpop_agg(mapunits, mapunits_id, subunits, mapunits_fk,
    indicator_col, pop_col, out_col, output):
    """
    Wheight indicator by pop and agregation
    Useful to calculate:
    Tempo medio ponderado pela populacao residente
    a infra-estrutura mais proxima
    """

    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    # Read data
    mapunits_df = shp_to_obj(mapunits)
    subunits_df = shp_to_obj(subunits)

    # Get population x indicator product
    subunits_df['prod'] = subunits_df[indicator_col] * subunits_df[pop_col]

    # Get product sum for each mapunit
    mapunits_prod = pd.DataFrame(subunits_df.groupby([mapunits_fk]).agg({
        'prod' : 'sum'
    })).reset_index()

    # Add product sum to subunits df
    mapunits_prod.rename(columns={
        mapunits_fk : 'jtblid', 'prod' : 'sumprod'
    }, inplace=True)

    subunits_df = subunits_df.merge(
        mapunits_prod, how='left', left_on=mapunits_fk,
        right_on='jtblid'
    )

    # Calculate wheighted indicator
    subunits_df[out_col] = (subunits_df['prod'] / subunits_df['sumprod']) * subunits_df[indicator_col]

    # Sum by mapunit
    mapunits_i = pd.DataFrame(subunits_df.groupby([mapunits_fk]).agg({
        out_col : 'sum'
    })).reset_index()
    mapunits_i.rename(columns={mapunits_fk : 'jtblid'}, inplace=True)

    mapunits_df = mapunits_df.merge(
        mapunits_i, how='left', left_on=mapunits_id,
        right_on='jtblid'
    )

    mapunits_df.drop(['jtblid'], axis=1, inplace=True)

    # Export result
    df_to_shp(mapunits_df, output)

    return output


def calc_weighted_mean(mapunits, muid, subunits, mufk, icol, wcol, ocol, output):
    """
    Weighted mean calculation

    Útil para calcular o tempo médio a uma infraestrutura
    por freguesia
    """

    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    # Read data
    mapunits_df = shp_to_obj(mapunits)
    subunits_df = shp_to_obj(subunits)

    # Get values/weight product
    subunits_df['prod'] = subunits_df[icol] * subunits_df[wcol]

    # Get sum of the last product and
    # sum of the weights
    munitsp = pd.DataFrame(subunits_df.groupby([mufk]).agg({
        'prod' : 'sum',
        wcol   : 'sum'
    })).reset_index()

    munitsp[ocol] = munitsp['prod'] / munitsp[wcol]

    munitsp.rename(columns={mufk : 'jtblid'}, inplace=True)
    munitsp.drop(['prod', wcol], axis=1, inplace=True)

    # Join data
    mapunits_df = mapunits_df.merge(
        munitsp, how='left', left_on=muid,
        right_on='jtblid'
    )

    mapunits_df.drop(['jtblid'], axis=1, inplace=True)

    # Export result
    df_to_shp(mapunits_df, output)

    return output


def points_by_polutation(pnt, mapunits, popcol, outcol, output,
    count_pnt=None, inhabitants=1000, pntattr=None):
    """
    Useful to calculate pharmacies by 1000 inabitants
    """
    
    from glass.rd.shp     import shp_to_obj
    from glass.prop.prj   import get_shp_epsg
    from glass.wt.shp     import obj_to_shp
    from glass.gp.ovl.obj import count_pnt_inside_poly

    # Open Data
    pnt_df   = shp_to_obj(pnt)
    units_df = shp_to_obj(mapunits)

    cpnt = 'count_pnt' if not count_pnt else count_pnt
    pntattr = None if not pntattr else pntattr \
        if pntattr in list(pnt_df.columns.values) else None
    inhabitants = 1 if not inhabitants else inhabitants

    units_df = count_pnt_inside_poly(pnt_df, cpnt, units_df, pntattr=pntattr)
    units_df[outcol] = (units_df[count_pnt] / units_df[popcol]) * inhabitants

    if not count_pnt:
        units_df.drop([cpnt], axis=1, inplace=True)
    
    obj_to_shp(units_df, "geometry", get_shp_epsg(mapunits), output)

    return output



def shparea_by_mapunitpopulation(polygons, mapunits, units_id, outcol, output,
    units_pop=None, areacol=None):
    """
    Polygons area by mapunit or by mapunit population
    """

    import os
    import geopandas         as gp
    from glass.dtr.ext.torst import shpext_to_rst
    from glass.pys.oss       import mkdir, fprop
    from glass.gp.ovl        import grsintersection
    from glass.prop.prj      import get_epsg
    from glass.wenv.grs      import run_grass
    from glass.rd.shp        import shp_to_obj
    from glass.wt.shp        import obj_to_shp

    delareacol = 1 if not areacol else 0
    areacol = outcol if not units_pop else areacol if areacol else 'areav'

    # Prepare GRASS GIS Workspace configuration
    oname = fprop(output, 'fn')

    gw = mkdir(os.path.join(
        os.path.dirname(output), 'ww_' + oname
    ), overwrite=True)

    # Boundary to raster
    w_epsg = get_epsg(mapunits) if type(mapunits) != gp.GeoDataFrame else \
        get_epsg(polygons)
    
    ref_rst = shpext_to_rst(
        mapunits, os.path.join(gw, 'extent.tif'),
        cellsize=10, epsg=w_epsg
    )

    # Sanitize columns
    popunits_df_tmp = shp_to_obj(mapunits) if type(mapunits) != gp.GeoDataFrame \
        else mapunits.copy(deep=True)

    drop_cols = [c for c in popunits_df_tmp.columns.values if c != units_id and c != 'geometry']
    popunits_df_tmp.drop(drop_cols, axis=1, inplace=True)

    popunits_i = obj_to_shp(popunits_df_tmp, 'geometry', w_epsg, os.path.join(
        gw, 'popunits.shp'
    ))

    # Create GRASS GIS Session
    _l = 'loc_' + oname

    gbase = run_grass(gw, location=_l, srs=ref_rst)

    import grass.script.setup as gsetup

    gsetup.init(gbase, gw, _l, 'PERMANENT')

    from glass.it.shp import shp_to_grs, grs_to_shp

    # Data to GRASS GIS
    g_popunits = shp_to_grs(
        popunits_i,
        fprop(mapunits, 'fn') if type(mapunits) != gp.GeoDataFrame \
            else 'mapunits_gdf',
        asCMD=True
    )
    g_polygons = shp_to_grs(polygons, fprop(polygons, 'fn'), asCMD=True)

    # Run intersection
    i_shp = grsintersection(
        g_popunits, g_polygons,
        f'i_{g_popunits[:5]}_{g_polygons[:5]}',
        cmd=True
    )

    # Export result
    i_res = grs_to_shp(i_shp, os.path.join(gw, i_shp + '.shp'), 'area')

    # Open intersection result and mapunits
    mapunits_df = shp_to_obj(mapunits) if type(mapunits) != gp.GeoDataFrame \
        else mapunits
    int_df      = shp_to_obj(i_res)

    int_df['garea'] = int_df.geometry.area

    int_gp = pd.DataFrame({
        areacol : int_df.groupby(['a_' + units_id])['garea'].agg('sum')
    }).reset_index()

    mapunits_df = mapunits_df.merge(
        int_gp, how='left',
        left_on=units_id, right_on='a_' + units_id
    )

    if units_pop:
        mapunits_df[outcol] = mapunits_df[areacol] / mapunits_df[units_pop]
        
    dc = ['a_' + units_id, areacol] if units_pop and delareacol else ['a_' + units_id]
    
    mapunits_df.drop(dc, axis=1, inplace=True)

    obj_to_shp(mapunits_df, 'geometry', w_epsg, output)

    return output

