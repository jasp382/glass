"""
ArcGIS Rest Services implementation for network analysis
"""

def closest_facility(incidents, incidents_id, facilities, output, impedance='TravelTime'):
    """
    impedance options:
    * TravelTime;
    * WalkTime;
    """

    import requests
    import pandas as pd
    import numpy as np
    from glass.cons.esri   import rest_token, CF_URL
    from glass.it.esri import json_to_gjson
    from glass.rd.shp    import shp_to_obj
    from glass.wt.shp    import df_to_shp
    from glass.pd.split import df_split
    from glass.pd       import merge_df
    from glass.prop.prj  import get_shp_epsg
    from glass.prj.obj   import df_prj
    from glass.it.pd     import df_to_geodf
    from glass.it.pd     import json_obj_to_geodf
    from glass.cons.esri   import get_tv_by_impedancetype

    # Get API token
    token = rest_token()

    # Data to Pandas DataFrames
    fdf = shp_to_obj(facilities)
    idf = shp_to_obj(incidents)

    # Re-project to WGS84
    fdf = df_prj(fdf, 4326)
    idf = df_prj(idf, 4326)

    # Geomtries to Str - inputs for requests
    fdf['coords'] = fdf.geometry.x.astype(str) + ',' + fdf.geometry.y.astype(str)
    idf['coords'] = idf.geometry.x.astype(str) + ',' + idf.geometry.y.astype(str)

    # Delete geometry from facilities DF
    idf.drop(['geometry'], axis=1, inplace=True)

    # Split data
    # ArcGIS API only accepts 100 facilities
    # # and 100 incidents in each request
    fdfs = df_split(fdf, 100, nrows=True) if fdf.shape[0] > 100 else [fdf]
    idfs = df_split(idf, 100, nrows=True) if idf.shape[0] > 100 else [idf]

    for i in range(len(idfs)):
        idfs[i].reset_index(inplace=True)
        idfs[i].drop(['index'], axis=1, inplace=True)
    
    for i in range(len(fdfs)):
        fdfs[i].reset_index(inplace=True)
        fdfs[i].drop(['index'], axis=1, inplace=True)
    
    # Get travel mode
    tv = get_tv_by_impedancetype(impedance)

    # Ask for results
    results = []

    drop_cols = [
        'ObjectID', 'FacilityID', 'FacilityRank', 'Name',
        'IncidentCurbApproach', 'FacilityCurbApproach', 'IncidentID', 'StartTime',
        'EndTime', 'StartTimeUTC', 'EndTimeUTC', 'Total_Minutes',
        'Total_TruckMinutes', 'Total_TruckTravelTime', 'Total_Miles'
    ]

    if impedance == 'WalkTime':
        tv_col  = 'walktime'
        rn_cols = {'Total_WalkTime' : tv_col}
        
        ndrop = ['Total_Kilometers', 'Total_TravelTime', 'Total_Minutes']
    
    elif impedance == 'metric':
        tv_col = 'kilomts'
        rn_cols = {'Total_Kilometers' : tv_col}

        ndrop = ['Total_WalkTime', 'Total_TravelTime', 'Total_Minutes']
    
    else:
        tv_col  = 'traveltime'
        rn_cols = {'Total_TravelTime' : tv_col}

        ndrop = ['Total_Kilometers', 'Total_WalkTime', 'Total_Minutes']

    drop_cols.extend(ndrop)

    for i_df in idfs:
        incidents_str  = i_df.coords.str.cat(sep=';')

        for f_df in fdfs:
            facilities_str = f_df.coords.str.cat(sep=';')

            # Make request
            r = requests.get(CF_URL, params={
                'facilities'             : facilities_str,
                'incidents'              : incidents_str,
                'token'                  : token,
                'f'                      : 'json',
                'travelModel'            : tv,
                'defaultTargetFacilityCount' : '1',
                'returnCFRoutes'        : True,
                'travelDirection'        : 'esriNATravelDirectionToFacility',
                'impedanceAttributeName' : impedance
            })

            if r.status_code != 200:
                raise ValueError(
                    'Error when requesting from: {}'.format(str(r.url))
                )
            
            # Convert ESRI json to GeoJson
            esri_geom = r.json()
            geom = json_to_gjson(esri_geom.get('routes'))

            # GeoJSON to GeoDataFrame
            gdf = json_obj_to_geodf(geom, 4326)

            # Delete unwanted columns
            gdf.drop(drop_cols, axis=1, inplace=True)

            # Rename some interest columns
            gdf.rename(columns=rn_cols, inplace=True)

            # Add to results original attributes of incidents
            r_df = gdf.merge(i_df, how='left', left_index=True, right_index=True)

            results.append(r_df)
    
    # Compute final result
    # Put every DataFrame in a single DataFrame
    fgdf = merge_df(results)

    # Since facilities were divided
    # The same incident has several "nearest" facilities
    # We just want one neares facility
    # Lets group by using min operator
    gpdf = pd.DataFrame(fgdf.groupby([incidents_id]).agg({
        tv_col : 'min'
    })).reset_index()

    gpdf.rename(columns={incidents_id : 'iid', tv_col : 'impcol'}, inplace=True)

    # Recovery geometry
    fgdf = fgdf.merge(gpdf, how='left', left_on=incidents_id, right_on='iid')
    fgdf = fgdf[fgdf[tv_col] == fgdf.impcol]
    fgdf = df_to_geodf(fgdf, 'geometry', 4326)

    # Remove repeated units
    g = fgdf.groupby('iid')
    fgdf['rn'] = g[tv_col].rank(method='first')
    fgdf = fgdf[fgdf.rn == 1]

    fgdf.drop(['iid', 'rn'], axis=1, inplace=True)

    # Re-project to original SRS
    epsg = get_shp_epsg(facilities)
    fgdf = df_prj(fgdf, epsg)

    # Export result
    df_to_shp(fgdf, output)

    return output


def cf_based_on_relations(incidents, incidents_id, group_incidents_col,
    facilities, facilities_id, rel_inc_fac, sheet, group_fk, facilities_fk,
    output, impedante='TravelTime'):
    """
    Calculate time travel considering specific facilities
    for each group of incidents

    Relations between incidents and facilities are in a auxiliar table (rel_inc_fac).
    Auxiliar table must be a xlsx file
    """

    import os
    import pandas       as pd
    from glass.rd       import tbl_to_obj
    from glass.rd.shp   import shp_to_obj
    from glass.wt.shp   import obj_to_shp
    from glass.prop.prj import get_shp_epsg
    from glass.pys.oss  import mkdir, fprop
    from glass.dp.mge   import shps_to_shp

    # Avoid problems when facilities_id == facilities_fk
    facilities_fk = facilities_fk + '_fk' if facilities_id == facilities_fk else \
        facilities_fk

    # Open data
    incidents_df  = shp_to_obj(incidents)
    facilities_df = shp_to_obj(facilities)

    rel_df = tbl_to_obj(rel_inc_fac, sheet=sheet)

    # Get SRS
    epsg = get_shp_epsg(incidents)

    # Create dir for temporary files
    tmpdir = mkdir(os.path.join(
        os.path.dirname(output), fprop(output, 'fn')
    ), overwrite=True)

    # Relate facilities with incidents groups
    facilities_df = facilities_df.merge(
        rel_df, how='inner',
        left_on=facilities_id, right_on=facilities_fk
    )

    # List Groups
    grp_df = pd.DataFrame({
        'cnttemp' : incidents_df.groupby([group_incidents_col])[group_incidents_col].agg('count')
    }).reset_index()

    # Do the calculations
    res = []
    for idx, row in grp_df.iterrows():
        # Get incidents for that group
        new_i = incidents_df[incidents_df[group_incidents_col] == row[group_incidents_col]]

        new_i = obj_to_shp(new_i, 'geometry', epsg, os.path.join(
            tmpdir, f'i_{row[group_incidents_col]}.shp'
        ))

        # Get facilities for that group
        new_f = facilities_df[facilities_df[group_fk] == row[group_incidents_col]]
        new_f = obj_to_shp(new_f, 'geometry', epsg, os.path.join(
            tmpdir, f'f_{row[group_incidents_col]}.shp'
        ))

        # calculate closest facility
        cf = closest_facility(
            new_i, incidents_id, new_f,
            os.path.join(tmpdir, f'cf_{row[group_incidents_col]}.shp')
        )

        res.append(cf)
    
    # Produce final result
    shps_to_shp(res, output, api="pandas")

    return output


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
    from glass.pd import merge_df
    from glass.prop.prj import get_shp_epsg

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
            raise ValueError(
                'Error when requesting from: {}'.format(str(r.url))
            )
    
        esri_geom = r.json()
        geom = json_to_gjson(esri_geom.get('saPolygons'))
    
        gdf = json_obj_to_geodf(geom, 4326)
    
        gdf = gdf.merge(df, how='left', left_index=True, right_index=True)
    
        gdfs.append(gdf)
    
    # Compute final result
    fgdf = merge_df(gdfs)

    epsg = get_shp_epsg(facilities)
    fgdf = df_prj(fgdf, epsg)

    df_to_shp(fgdf, output)

    return output

