"""
Produce indicators
"""

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
    import pandas as pd
    from glass.dct.geo.fmshp  import shp_to_obj
    from glass.dct.geo.torst  import shpext_to_rst
    from glass.dct.geo.toshp  import obj_to_shp
    from glass.pys.oss        import mkdir, fprop
    from glass.geo.df.gop.ovl import intersection
    from glass.geo.prop.prj   import get_epsg
    from glass.geo.wenv.grs   import run_grass

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

    import grass.script as grass
    import grass.script.setup as gsetup

    gsetup.init(gbase, gw, loc, 'PERMANENT')

    from glass.dct.geo.toshp.cff import shp_to_grs, grs_to_shp

    # Send data to GRASS GIS
    grs_res = shp_to_grs(
        res_areas if res_areas and res_areas_fk else subunits,
        fprop(res_areas if res_areas and res_areas_fk else subunits, 'fn'),
        asCMD=True
    )
    grs_ash = shp_to_grs(area_shp, fprop(area_shp, 'fn'), asCMD=True)

    # Run intersection
    int_ = intersection(grs_res, grs_ash, 'i_{}_{}'.format(
        grs_res, grs_ash
    ), api='grass')

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

    import pandas as pd
    from glass.dct.geo.fmshp import shp_to_obj
    from glass.dct.geo.toshp import df_to_shp

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

