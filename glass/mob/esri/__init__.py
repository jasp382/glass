"""
ArcGIS Rest Services implementation for network analysis
"""

import os


def service_areas(facilities, breaks, output, impedance='TravelTime', towardsFacility=True, highDetail=None):
    """
    Produce Service Areas Polygons

    https://developers.arcgis.com/documentation/mapping-and-location-services/routing-and-directions/service-areas/
    https://developers.arcgis.com/rest/routing/service-area-synchronous-service/
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
    from glass.wt.js      import dict_to_json
    from glass.pys.tm import now_as_str

    # Get Token
    token = rest_token()

    # Get data
    pntdf = shp_to_obj(facilities)

    pntdf = df_prj(pntdf, 4326)

    pntdf['coords'] = pntdf.geometry.x.astype(str) + ',' + pntdf.geometry.y.astype(str)

    pntdf.drop(['geometry'], axis=1, inplace=True)

    dfs = df_split(pntdf, 100, nrows=True)

    _breaks = [str(b) for b in breaks]

    tvdirection = 'esriNATravelDirectionToFacility' if towardsFacility \
        else 'esriNATravelDirectionFromFacility'
    
    detail = 'esriNAOutputPolygonSimplified' if not highDetail else \
        'esriNAOutputPolygonDetailed'

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
            'defaultBreaks'          : ','.join(_breaks),
            'travelDirection'        : tvdirection,
            #'travelDirection'        : 'esriNATravelDirectionFromFacility',
            #'outputPolygons'         : 'esriNAOutputPolygonDetailed',
            'outputPolygons'         : detail,
            'impedanceAttributeName' : impedance,
            'overlapPolygons'        : False,
            'restrictUTurns'         : 'esriNFSBNoBacktrack'
        })
    
        if r.status_code != 200:
            raise ValueError(f'Error when requesting from: {str(r.url)}')
    
        esri_geom = r.json()
        dict_to_json(esri_geom, os.path.join(
            os.path.dirname(output),
            f"esri_sa_response_{now_as_str()}.json"
        ))
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

