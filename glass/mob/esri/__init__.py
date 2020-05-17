"""
ArcGIS Rest Services implementation for network analysis
"""


def service_areas(facilities, breaks, output, impedance='TravelTime'):
    """
    Produce Service Areas Polygons
    """

    import requests
    from glass.cons.esri import rest_token, SA_URL
    from glass.rd.shp import shp_to_obj
    from glass.prj.obj import df_prj
    from glass.it.esri import json_to_gjson
    from glass.it.pd import json_obj_to_geodf
    from glass.wt.shp import df_to_shp
    from glass.cons.esri import get_tv_by_impedancetype
    from glass.pd.split import df_split
    from glass.dtt.mge.pd import merge_df
    from glass.prop.prj import shp_epsg

    # Get Token
    token = rest_token()

    # Get data
    pntdf = shp_to_obj(facilities)

    pntdf = df_prj(pntdf, 4326)

    pntdf['coords'] = pntdf.geometry.x.astype(str) + ',' + pntdf.geometry.y.astype(str)

    pntdf.drop(['geometry'], axis=1, inplace=True)

    dfs = df_split(pntdf, 100, nrows=True)

    # Make requests
    gdfs = []
    for df in dfs:
        facilities_str = df.coords.str.cat(sep=';')
    
        tv = get_tv_by_impedancetype(impedance)

        r = requests.get(SA_URL, params={
            'facilities'             : facilities_str,
            'token'                  : token,
            'f'                      : 'json',
            'travelModel'            : tv,
            'defaultBreaks'          : ','.join(breaks),
            'travelDirection'        : 'esriNATravelDirectionToFacility',
            #'travelDirection'        : 'esriNATravelDirectionFromFacility',
            'outputPolygons'         : 'esriNAOutputPolygonDetailed',
            'impedanceAttributeName' : impedance
        })
    
        if r.status_code != 200:
            raise ValueError(f'Error when requesting from: {str(r.url)}')
    
        esri_geom = r.json()
        geom = json_to_gjson(esri_geom.get('saPolygons'))
    
        gdf = json_obj_to_geodf(geom, 4326)
    
        gdf = gdf.merge(df, how='left', left_index=True, right_index=True)
    
        gdfs.append(gdf)
    
    # Compute final result
    fgdf = merge_df(gdfs)

    epsg = shp_epsg(facilities)
    fgdf = df_prj(fgdf, epsg)

    df_to_shp(fgdf, output)

    return output

