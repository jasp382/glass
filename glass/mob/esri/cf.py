"""
ArcGIS Rest Services implementation for network analysis

Closest facilities implementations
"""

import os
import pandas    as pd
import geopandas as gp
import requests  as rq
import json      as js

from glass.cons.esri  import rest_token, CF_URL
from glass.cons.esri  import get_tv_by_impedancetype
from glass.it.esri    import json_to_gjson
from glass.rd.shp     import shp_to_obj
from glass.prj.obj    import df_prj
from glass.pd.split   import df_split
from glass.wt.js      import dict_to_json
from glass.wt.shp     import df_to_shp
from glass.dtr.mge.pd import merge_df
from glass.prop.prj   import get_shp_epsg
from glass.it.pd      import df_to_geodf
from glass.it.pd      import json_obj_to_geodf


def closest_facility(incidents, incidents_id, facilities, output,
    impedance='TravelTime', crs=None, save_temp_json=None):
    """
    impedance options:
    * TravelTime;
    * WalkTime;
    """

    iauxid = 'iid' if incidents_id != 'iid' else 'fiid'

    # Get API token
    token = rest_token()

    # Data to Pandas DataFrames
    fdf = shp_to_obj(facilities) if type(facilities) != gp.GeoDataFrame else facilities
    idf = shp_to_obj(incidents) if type(incidents) != gp.GeoDataFrame else incidents

    # Re-project to WGS84
    fdf = df_prj(fdf, 4326)
    idf = df_prj(idf, 4326)

    # Geometries to Str - inputs for requests
    fdf['coords'] = fdf.geometry.x.astype(str) + ',' + fdf.geometry.y.astype(str)
    idf['coords'] = idf.geometry.x.astype(str) + ',' + idf.geometry.y.astype(str)

    # Delete geometry from facilities DF
    idf.drop(['geometry'], axis=1, inplace=True)

    # Split data
    # ArcGIS API only accepts 100 facilities
    # and 100 incidents in each request
    fdfs = df_split(fdf, 100, nrows=True) if fdf.shape[0] > 100 else [fdf]
    idfs = df_split(idf, 100, nrows=True) if idf.shape[0] > 100 else [idf]

    for i in range(len(idfs)):
        idfs[i].reset_index(inplace=True, drop=True)
    
    for i in range(len(fdfs)):
        fdfs[i].reset_index(inplace=True, drop=True)
    
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
        
        ndrop = ['Total_Kilometers']
    
    elif impedance == 'metric':
        tv_col = 'kilomts'
        rn_cols = {'Total_Kilometers' : tv_col}

        ndrop = ['Total_WalkTime', 'Total_TravelTime', 'Total_Minutes']
    
    else:
        tv_col  = 'traveltime'
        rn_cols = {'Total_TravelTime' : tv_col}

        ndrop = ['Total_Kilometers', 'Total_WalkTime', 'Total_Minutes']

    drop_cols.extend(ndrop)

    _c = 1
    for i_df in idfs:
        incidents_str  = i_df.coords.str.cat(sep=';')

        for f_df in fdfs:
            facilities_str = f_df.coords.str.cat(sep=';')

            # Make request
            r = rq.get(CF_URL, params={
                'facilities'             : facilities_str,
                'incidents'              : incidents_str,
                'token'                  : token,
                'f'                      : 'json',
                'travelModel'            : js.dumps(tv),
                'defaultTargetFacilityCount' : '1',
                'returnCFRoutes'         : True,
                'travelDirection'        : 'esriNATravelDirectionToFacility',
                'impedanceAttributeName' : impedance
            })

            if r.status_code != 200:
                raise ValueError(f'Error when requesting from: {str(r.url)}')
            
            # Convert ESRI json to GeoJson
            esri_geom = r.json()

            if save_temp_json:
                dict_to_json(esri_geom, os.path.join(
                    os.path.dirname(output),
                    f"esri_response_{str(_c)}.json"
                ))

            geom = json_to_gjson(esri_geom.get('routes'))

            # GeoJSON to GeoDataFrame
            gdf = json_obj_to_geodf(geom, 4326)

            # Delete unwanted columns
            ndc = [c for c in drop_cols if c in gdf.columns.values]
            gdf.drop(ndc, axis=1, inplace=True)

            # Rename some interest columns
            gdf.rename(columns=rn_cols, inplace=True)

            # Add to results original attributes of incidents
            r_df = gdf.merge(i_df, how='left', left_index=True, right_index=True)

            results.append(r_df)
        
            _c += 1
    
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

    gpdf.rename(columns={incidents_id : iauxid, tv_col : 'impcol'}, inplace=True)

    # Recovery geometry
    fgdf = fgdf.merge(gpdf, how='left', left_on=incidents_id, right_on=iauxid)
    fgdf = fgdf[fgdf[tv_col] == fgdf.impcol]
    fgdf = df_to_geodf(fgdf, 'geometry', 4326)

    # Remove repeated units
    g = fgdf.groupby(iauxid)
    fgdf['rn'] = g[tv_col].rank(method='first')
    fgdf = fgdf[fgdf.rn == 1]

    fgdf.drop([iauxid, 'rn'], axis=1, inplace=True)

    # Re-project to original SRS
    if type(facilities) != gp.GeoDataFrame:
        epsg = get_shp_epsg(facilities)
    
    else:
        epsg = 4326 if not crs else crs
    fgdf = df_prj(fgdf, epsg)

    # Export result
    df_to_shp(fgdf, output)

    return output


def cf_based_on_relations(incidents, incidents_id, group_incidents_col,
    facilities, facilities_id, rel_inc_fac, sheet, group_fk, facilities_fk,
    output, impedance='TravelTime'):
    """
    Calculate time travel considering specific facilities
    for each group of incidents

    Relations between groups of incidents and facilities
     are in a auxiliar table (rel_inc_fac).
    Auxiliar table must be a xlsx file
    """
    
    from glass.rd       import tbl_to_obj
    from glass.rd.shp   import shp_to_obj
    from glass.wt.shp   import obj_to_shp
    from glass.prop.prj import get_shp_epsg
    from glass.pys.oss  import mkdir, fprop
    from glass.dtr.mge  import shps_to_shp

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
            os.path.join(tmpdir, f'cf_{row[group_incidents_col]}.shp'),
            impedance=impedance,
            save_temp_json=True
        )

        res.append(cf)
    
    # Produce final result
    shps_to_shp(res, output, api="pandas")

    return output


def cf_ign_distfac(incidents, incidents_id, facilities, output,
                   save_temp_json=None, crs=None):
    """
    Closest facilities implementation:

    Ignores facilities away from incidents more than
    43 km
    """

    # Global Stuff
    impedance = 'WalkTime'
    iauxid    = 'iid' if incidents_id != 'iid' else 'fiid'
    # Get travel mode
    tv = get_tv_by_impedancetype(impedance)
    tv_col  = 'walktime'
    rn_cols = {'Total_WalkTime' : tv_col}

    drop_cols = [
        'ObjectID', 'FacilityID', 'FacilityRank', 'Name',
        'IncidentCurbApproach', 'FacilityCurbApproach', 'IncidentID', 'StartTime',
        'EndTime', 'StartTimeUTC', 'EndTimeUTC', 'Total_Minutes',
        'Total_TruckMinutes', 'Total_TruckTravelTime', 'Total_Miles'
    ]

    ndrop = ['Total_Kilometers']

    drop_cols.extend(ndrop)

    # Get API token
    token = rest_token()

    # Data to Pandas DataFrames
    fdf = shp_to_obj(facilities) if type(facilities) != gp.GeoDataFrame else facilities
    idf = shp_to_obj(incidents) if type(incidents) != gp.GeoDataFrame else incidents

    # Get Groups of incidents and incidents
    # that can be processed together because they are
    # distant at least 43 Km from each other

    # Merge dataframes
    # Relate all lines to all lines
    fdf['auxcol'] = 1
    idf['auxcol'] = 1
    idf['fid_a'] = idf.index + 1
    fdf['fid_b'] = fdf.index + 1

    adf = idf.merge(fdf, how='inner', on='auxcol').drop('auxcol', axis=1)

    # Calculate distance between incidents and facilities
    geom_i = gp.GeoSeries(adf.geometry_x)
    geom_f = gp.GeoSeries(adf.geometry_y)

    adf["dist"] = geom_i.distance(geom_f, align=True) / 1000

    # Exclude distances greater than 43 Km
    adf = adf[adf.dist < 25]
    adf = adf[['fid_a', 'fid_b']]

    # Get groups
    adf = adf.groupby('fid_a')['fid_b'].apply(list).reset_index(name='fid_b')
    adf['fid_b'] = adf.fid_b.apply(lambda x: sorted(x))
    adf = adf.groupby(adf.fid_b.map(tuple))['fid_a'].apply(list).reset_index(name='fid_a')

    # Re-project to WGS84
    fdf = df_prj(fdf, 4326)
    idf = df_prj(idf, 4326)

    # Geometries to Str - inputs for requests
    fdf['coords'] = fdf.geometry.x.astype(str) + ',' + fdf.geometry.y.astype(str)
    idf['coords'] = idf.geometry.x.astype(str) + ',' + idf.geometry.y.astype(str)

    # Delete geometry from facilities DF
    idf.drop(['geometry'], axis=1, inplace=True)

    results = []

    # For each set of groups
    for i, group in adf.iterrows():
        # Get subset of incidents and facilities
        inc = idf[idf['fid_a'].isin(group.fid_a)]
        inc.reset_index(inplace=True, drop=True)
        fac = fdf[fdf['fid_b'].isin(group.fid_b)]
        fac.reset_index(inplace=True, drop=True)

        # Split data
        # ArcGIS API only accepts 100 facilities
        # and 100 incidents in each request
        fdfs = df_split(fac, 100, nrows=True) if fac.shape[0] > 100 else [fac]
        idfs = df_split(inc, 100, nrows=True) if inc.shape[0] > 100 else [inc]

        # Go for analysis
        _c = 1
        for i_df in idfs:
            incidents_str  = i_df.coords.str.cat(sep=';')

            for f_df in fdfs:
                facilities_str = f_df.coords.str.cat(sep=';')

                # Make request
                r = rq.get(CF_URL, params={
                    'facilities'             : facilities_str,
                    'incidents'              : incidents_str,
                    'token'                  : token,
                    'f'                      : 'json',
                    'travelModel'            : js.dumps(tv),
                    'defaultTargetFacilityCount' : '1',
                    'returnCFRoutes'         : True,
                    'travelDirection'        : 'esriNATravelDirectionToFacility',
                    'impedanceAttributeName' : impedance
                })

                if r.status_code != 200:
                    raise ValueError(f'Error when requesting from: {str(r.url)}')
                
                # Convert ESRI json to GeoJson
                esri_geom = r.json()

                if save_temp_json:
                    dict_to_json(esri_geom, os.path.join(
                        os.path.dirname(output),
                        f"esri_response_{str(i)}_{str(_c)}.json"
                    ))
                
                geom = json_to_gjson(esri_geom.get('routes'))

                # GeoJSON to GeoDataFrame
                gdf = json_obj_to_geodf(geom, 4326)

                # Delete unwanted columns
                ndc = [c for c in drop_cols if c in gdf.columns.values]
                gdf.drop(ndc, axis=1, inplace=True)

                # Rename some interest columns
                gdf.rename(columns=rn_cols, inplace=True)

                # Add to results original attributes of incidents
                r_df = gdf.merge(i_df, how='left', left_index=True, right_index=True)

                results.append(r_df)

                _c +=1
    
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

    gpdf.rename(columns={incidents_id : iauxid, tv_col : 'impcol'}, inplace=True)

    # Recovery geometry
    fgdf = fgdf.merge(gpdf, how='left', left_on=incidents_id, right_on=iauxid)
    fgdf = fgdf[fgdf[tv_col] == fgdf.impcol]
    fgdf = df_to_geodf(fgdf, 'geometry', 4326)

    # Remove repeated units
    g = fgdf.groupby(iauxid)
    fgdf['rn'] = g[tv_col].rank(method='first')
    fgdf = fgdf[fgdf.rn == 1]

    fgdf.drop([iauxid, 'rn'], axis=1, inplace=True)

    # Re-project to original SRS
    if type(facilities) != gp.GeoDataFrame:
        epsg = get_shp_epsg(facilities)
    
    else:
        epsg = 4326 if not crs else crs
    fgdf = df_prj(fgdf, epsg)

    # Export result
    df_to_shp(fgdf, output)

    return output

