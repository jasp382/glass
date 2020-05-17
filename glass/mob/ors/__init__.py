"""
Open Route Service Related
"""

import requests as rq

from glass.cons.ors import MAIN_URL
from glass.cons.ors import get_ors_token
from glass.pys.web import http_to_json


"""
Open Route Service API Data Processing
"""

"""
Open Route Service tools
"""



def directions(lat_o, lng_o, lat_d, lng_d, modeTransportation='foot-walking'):
    """
    Get Shortest path between two points using Directions service
    
    profile options:
    * driving-car;
    * driving-hgv;
    * cycling-regular;
    * cycling-road;
    * cycling-safe;
    * cycling-mountain;
    * cycling-tour;
    * cycling-electric;
    * foot-walking;
    * foot-hiking;
    * wheelchair.
    
    preference options:
    * fastest, shortest, recommended
    
    format options: geojson, gpx
    
    DOC: https://openrouteservice.org/documentation/#/authentication/UserSecurity
    """

    key = get_ors_token()
    
    URL = (
        f"{MAIN_URL}directions?api_key={key}&"
        f"coordinates={lng_o},{lat_o}|{lng_d},{lat_d},&"
        f"profile={modeTransportation}&preferences=fastest&"
        "format=geojson"
    )
    
    data = http_to_json(URL)
    
    return data


def isochrones(locations, range, range_type='time',
               modeTransportation='foot-walking',
               intervals=None, useKey=None):
    """
    Obtain areas of reachability from given locations
    
    The Isochrone Service supports time and distance analyses for one
    single or multiple locations. You may also specify the isochrone
    interval or provide multiple exact isochrone range values.
    This service allows the same range of profile options listed in the
    ORS Routing section which help you to further customize your request
    to obtain a more detailed reachability area response.
    """

    key = get_ors_token()
    
    url_intervals = f"&interval={str(intervals)}" if intervals \
        else ""
    
    API_KEY_TO_USE = key if not useKey else useKey
    
    URL = (
        "{_url_}isochrones?api_key={apik}&"
        "locations={loc}&profile={transport}&range_type={rng_type}&"
        "range={rng}{_int}"
    ).format(
        _url_=MAIN_URL, apik=API_KEY_TO_USE,
        loc=locations, transport=modeTransportation,
        rng_type=range_type, rng=range,
        _int=url_intervals
    )
    
    data = http_to_json(URL)
    
    return data

def isochrones_to_file(locations, range, outFile,
               modeTransportation='foot-walking',
               intervals=None, range_type='time'):
    
    import json
    
    data = isochrones(
        locations, range, range_type,
        modeTransportation=modeTransportation,
        intervals=intervals
    )
    
    with open(outFile, 'w') as j:
        json.dump(data, j)
    
    return outFile


def matrix_od(locations, idx_src="all", idx_dest="all",
              impedance='foot-walking'):
    """
    Execute Matrix Service
    """
    
    key = get_ors_token()

    body = {
        "locations"    : locations,
        "destinations" : idx_dest,
        "sources"      : idx_src
    }

    headers = {
        'Accept'        : 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization' : key,
        'Content-Type'  : 'application/json; charset=utf-8'
    }
    
    url = f"{MAIN_URL}matrix/{impedance}"
    
    rsp = rq.post(url, json=body, headers=headers)

    code, reas = rsp.status_code, rsp.reason

    if code == 200:
        return {
            "code" : code, "json" : rsp.json(),
            "reason" : reas, 'text' : None
        }
    
    else:
        return {
            "code" : code, "json" : None,
            "reason" : reas, 'text' : rsp.ext
        }


def path_from_coords_to_shp(latOrigin, lngOrigin, latDest, lngDest, outshp,
                            transmod='foot-walking', outepsg=4326):
    """
    Receive coords and get path. Save path as Feature Class
    """
    
    import pandas
    from glass.it.pd  import df_to_geodf, json_obj_to_geodf
    from glass.wt.shp import df_to_shp
    
    path = directions(
        latOrigin, lngOrigin, latDest, lngDest,
        modeTransportation=transmod
    )
    
    geodf = json_obj_to_geodf(path, 4326)
    
    geodf.drop(['segments', 'bbox', 'way_points'], axis=1, inplace=True)
    
    geodf["summary"] = geodf['summary'][0]
    
    geodf = pandas.concat([
        geodf.drop(['summary'], axis=1),
        geodf['summary'].apply(pandas.Series)
    ], axis=1)
    
    geodf = df_to_geodf(geodf, "geometry", 4326)
    
    if outepsg != 4326:
        from glass.prj import proj
        geodf = proj(geodf, None, outepsg, api='pandas')
    
    return df_to_shp(geodf, outshp)


def servarea_from_points(pntShp, inEPSG, range, outShp,
                         mode='foot-walking', intervals=None):
    """
    Calculate isochrones for all points in a Point Feature Class
    """
    
    import time
    from threading        import Thread
    from shapely.geometry import shape

    from glass.rd         import tbl_to_obj
    from glass.pd.split   import df_split
    from glass.dtt.mge.pd import merge_df
    from glass.prop.feat  import get_gtype
    from glass.prj        import proj
    from glass.pd         import df_to_dict
    from glass.wt.shp     import df_to_shp
    from glass.tbl.col    import pointxy_to_cols
    from glass.it.pd      import obj_to_geodf
    
    # SHP TO GEODATAFRAME
    pntDf = tbl_to_obj(pntShp)
    
    # Check if SHPs are points
    inGeomType = get_gtype(pntDf, geomCol="geometry", gisApi='pandas')
    
    if inGeomType != 'Point' and inGeomType != 'MultiPoint':
        raise ValueError('The input geometry must be of type point')
    
    # Reproject geodf if necessary
    if inEPSG != 4326:
        pntDf = proj(pntDf, None, 4326, api='pandas')
    
    pntDf["old_fid"] = pntDf.index
    
    pntDf = pointxy_to_cols(
        pntDf, geomCol="geometry",
        colX="longitude", colY="latitude"
    )
    
    # Get Keys
    KEYS = get_keys()
    
    df_by_key = df_split(pntDf, KEYS.shape[0])
    
    keys_list = KEYS['key'].tolist()
    
    results = []
    
    def get_isochrones(df, key):
        pntDict = df_to_dict(df)
    
        for k in pntDict:
            iso = isochrones(
                f'{pntDict[k]["longitude"]},{pntDict[k]["latitude"]}',
                range, range_type='time', modeTransportation=mode,
                intervals=intervals
            )
        
            pntDict[k]["geometry"] = shape(iso["features"][0]["geometry"])
        
            time.sleep(5)
    
            pntDf = obj_to_geodf(pntDict, "geometry", 4326)
        
        results.append(pntDf)
    
    # Create threads
    thrds = []
    i = 1
    for df in df_by_key:
        thrds.append(Thread(
            name=f'tk{str(i)}', target=get_isochrones,
            args=(df, keys_list[i - 1])
        ))
        i += 1
    
    # Start all threads
    for thr in thrds:
        thr.start()
    
    # Wait for all threads to finish
    for thr in thrds:
        thr.join()
    
    # Join all dataframes
    pntDf = merge_df(results, ignIndex=False)
    
    if inEPSG != 4326:
        pntDf = proj(pntDf, None, inEPSG, api='pandas')
    
    return df_to_shp(pntDf, outShp)


def cost_od(shpOrigins, shpDestinations, epsgOrigins, epsgDestinations,
            table_result, mode='foot-walking'):
    """
    Matrix od Service Implementation
    """
    
    import pandas
    from threading        import Thread
    from glass.rd         import tbl_to_obj
    from glass.pd.split   import df_split
    from glass.tbl.col    import pointxy_to_cols
    from glass.prj        import proj
    from glass.dtt.mge.pd import merge_df
    from glass.prop.feat  import get_gtype
    from glass.wt         import obj_to_tbl
    
    origensDf = tbl_to_obj(     shpOrigins)
    destinoDf = tbl_to_obj(shpDestinations)
    
    # Check if SHPs are points
    inGeomType = get_gtype(origensDf, geomCol="geometry", gisApi='pandas')
    
    if inGeomType != 'Point' and inGeomType != 'MultiPoint':
        raise ValueError('The input geometry must be of type point')
    
    inGeomType = get_gtype(destinoDf, geomCol="geometry", gisApi='pandas')
    
    if inGeomType != 'Point' and inGeomType != 'MultiPoint':
        raise ValueError('The input geometry must be of type point')
    
    # Re-project if needed
    if epsgOrigins != 4326:
        origensDf = proj(origensDf, None, 4326, api='pandas')
    
    if epsgDestinations != 4326:
        destinoDf = proj(destinoDf, None, 4326, api='pandas')
    
    origensDf = pointxy_to_cols(
        origensDf, geomCol="geometry",
        colX="longitude", colY="latitude"
    ); destinoDf = pointxy_to_cols(
        destinoDf, geomCol="geometry",
        colX="longitude", colY="latitude"
    )
    
    origensDf["location"] = origensDf.longitude.astype(str) + "," + \
        origensDf.latitude.astype(str)
    destinoDf["location"] = destinoDf.longitude.astype(str) + "," + \
        destinoDf.latitude.astype(str)
    
    origensDf["old_fid"] = origensDf.index
    destinoDf["old_fid"] = destinoDf.index
    
    # Get Keys
    KEYS = get_keys()

    origensByKey = df_split(origensDf, KEYS.shape[0])

    lst_keys = KEYS["key"].tolist()
    
    # Produce matrix
    results = []
    def get_matrix(origins, key):
        origins.reset_index(inplace=True)
        origins["rqst_idx"] = origins.index.astype(str)
        
        destinations = destinoDf.copy()
        
        strSource = origins.location.str.cat(sep="|")
        idxSource = origins.rqst_idx.str.cat(sep=",")
        
        destinations["rqst_idx"] = destinations.old_fid + origins.shape[0]
        destinations["rqst_idx"] = destinations.rqst_idx.astype(str)
        strDestin = destinations.location.str.cat(sep="|")
        idxDestin = destinations.rqst_idx.str.cat(sep=",")
        
        rslt = matrix_od(
            strSource + "|" + strDestin,
            idxSources=idxSource, idxDestinations=idxDestin,
            useKey=key, modeTransportation=mode
        )
        
        rslt = pandas.DataFrame(rslt["durations"])
        
        originsFID = origins.old_fid.tolist()
        destinaFID = destinations.old_fid.tolist()
        
        mm = []
        for lnh in range(len(originsFID)):
            for col in range(len(destinaFID)):
                ll = [
                    originsFID[lnh], destinaFID[col], rslt.iloc[lnh, col]
                ]
                mm.append(ll)
        
        matrix = pandas.DataFrame(
            mm, columns=["fid_origin", "fid_destin", "cost"])
        
        results.append(matrix)
    
    # Create threads
    thrds = []
    i= 1
    for df in origensByKey:
        thrds.append(Thread(
            name=f"tk{str(i)}", target=get_matrix,
            args=(df, lst_keys[i - 1])
        ))
        i += 1
    
    # Start all threads
    for thr in thrds:
        thr.start()
    
    # Wait for all threads to finish
    for thr in thrds:
        thr.join()
    
    # Join all dataframes
    RESULT = merge_df(results, ignIndex=False)
    
    RESULT = RESULT.merge(
        origensDf             , how='inner',
        left_on=["fid_origin"], right_on=["old_fid"]
    ); RESULT.drop([
        x for x in origensDf.columns.values if x != "geometry"],
        axis=1, inplace=True
    ); RESULT.rename(columns={"geometry" : "origin_geom"}, inplace=True)
    
    RESULT = RESULT.merge(
        destinoDf, how='inner',
        left_on=["fid_destin"], right_on=["old_fid"]
    ); RESULT.drop([
        x for x in destinoDf.columns.values if x != "geometry"],
        axis=1, inplace=True
    ); RESULT.rename(columns={"geometry" : "destin_geom"}, inplace=True)
    
    RESULT["origin_geom"] = RESULT.origin_geom.astype(str)
    RESULT["destin_geom"] = RESULT.destin_geom.astype(str)
    
    return obj_to_tbl(RESULT, table_result)

