"""
Methods to extract data from Twitter
"""

def search_tweets(lat=None, lng=None, radius=None, keyword=None,
                  NR_ITEMS=500, only_geo=None, __lang=None, key=None,
                  resultType='mixed', drop_cols=None, in_geom=None, epsg=None):
    """
    Basic tool to extract data from Twitter using a keyword and/or a buffer
    
    * radius should be in Km
    * options for resulType: mixed, recent, popular
    
    Returns an array with the encountered data
    """
    
    import tweepy;       import pandas as pd
    from glass.pd.cols import listval_to_newcols
    from glass.pys       import obj_to_lst

    if not lat and not lng and not radius and not in_geom and not keyword:
        raise ValueError('No query parameters were provided. Nothing to do')

    if in_geom and not epsg:
        raise ValueError('inGeom implies epsg')

    if lat:
        if not lng or not radius:
            raise ValueError('lat implies lng and radius')
    
    if lng:
        if not lat or not radius:
            raise ValueError('lng implies lat and radius')
    
    if radius:
        if not lat or not lng:
            raise ValueError('radius implies lat and lng')
    
    if in_geom:
        from glass.prop.feat.bf import getBufferParam

        lng, lat, radius = getBufferParam(in_geom, epsg, outSRS=4326)

        radius = float(radius) / 1000
    
    if not key:
        from glass.cons.dsn import tw_key

        key = tw_key(allkeys=False)

    TOKEN, SECRET, CONSUMER_KEY, CONSUMER_SECRET = key['TOKEN'],\
        key['SECRET'], key['CONSUMER_KEY'], key['CONSUMER_SECRET']
    
    resultType = None if resultType == 'mixed' else resultType
    
    # Give our credentials to the Twitter API
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    
    auth.set_access_token(TOKEN, SECRET)
    
    api = tweepy.API(auth)
    
    # Request data from twitter
    keyword = '' if not keyword else keyword
    
    if not lat or not lng or not radius:
        data = [i._json for i in tweepy.Cursor(
            api.search, q=keyword, lang=__lang, count=50,
            result_type=resultType
        ).items(NR_ITEMS)]
    
    else:
        __geostr = f'{str(lat)},{str(lng)},{str(radius)}km'
        
        data = [i._json for i in tweepy.Cursor(
            api.search, q=keyword, geocode=__geostr, lang=__lang,
            count=50, result_type=resultType
        ).items(NR_ITEMS)]
    
    data = pd.DataFrame(data)
    
    if not data.shape[0]:
        return data
    
    data.rename(columns={
        "id"   : "fid", "created_at" : "tweet_time",
        "lang" : "tweet_lang"
    }, inplace=True)
    
    if "place" in data.columns.values:
        from shapely.geometry import shape
        
        def get_wkt(x):
            if type(x) == dict:
                g = shape(x)
            
                return str(g.wkt)
            
            else:
                return 'None'
        
        # Split in several columns
        data = listval_to_newcols(data, "place")
        
        cols = list(data.columns.values)
        colsRename = {}
        for c in cols:
            if c == "name":
                colsRename[c] = "place_name"
            elif c == "country":
                colsRename[c] = "place_country"
            elif c == "country_code":
                colsRename[c] = "place_countryc"
            elif c == "id":
                colsRename[c] = "place_id"
            else:
                continue
        
        data.rename(columns=colsRename, inplace=True)
        
        if 'bounding_box' in data.columns.values:
            data.loc[:, "place_box"] = data.bounding_box.apply(get_wkt)
        
        else:
            data.loc[:, "place_box"] = 'None'
    
    cols = list(data.columns.values)
    
    INTEREST_COLS = [
        'user', 'text', 'fid', 'geo', 'tweet_time', 'retweeted',
        'tweet_lang', 'place_name', 'place_country', 'place_countryc',
        'place_id', 'place_box'
    ]
    
    delCols = [x for x in cols if x not in INTEREST_COLS]
    
    data.drop(delCols, axis=1, inplace=True)
    
    dfGeom = data[data.geo.astype(str) != 'None']
    
    if only_geo and not dfGeom.shape[0]:
        return dfGeom
    
    elif not only_geo and not dfGeom.shape[0]:
        result = data
        
        result.loc[:, "latitude"]  = result.geo
        result.loc[:, "longitude"] = result.geo
        result.drop("geo", axis=1, inplace=True)
    
    else:
        dfGeom = pd.concat([
            dfGeom.drop(["geo"], axis=1),
            dfGeom.geo.apply(pd.Series)
        ], axis=1)
        
        dfGeom = pd.concat([
            dfGeom.drop(["coordinates"], axis=1),
            dfGeom.coordinates.apply(pd.Series)
        ], axis=1)
        
        dfGeom.rename(columns={0 : 'latitude', 1 : 'longitude'}, inplace=True)
        
        dfGeom.drop("type", axis=1, inplace=True)
        
        if only_geo:
            result = dfGeom
        
        else:
            dfNoGeom = data[data.geo.astype(str) == 'None']
            dfNoGeom.loc[:, "latitude"]  = dfNoGeom.geo
            dfNoGeom.loc[:, "longitude"] = dfNoGeom.geo
            
            dfNoGeom.drop("geo", axis=1, inplace=True)
            
            result = dfGeom.append(dfNoGeom, ignore_index=True)
    
    result = pd.concat([
        result.drop(["user"], axis=1),
        result["user"].apply(pd.Series)
    ], axis=1)
    
    result.rename(columns={
        'screen_name' : 'user', 'id' : 'user_id', 'location' : 'user_location',
        'name' : 'username'
    }, inplace=True)
    
    INTEREST_COLS += [
        'followers_count', 'user_id', 'user_location', 'username',
        'latitude', 'longitude'
    ]
    cols = list(result.columns.values)
    delCols = [c for c in cols if c not in INTEREST_COLS]
    
    result.drop(delCols, axis=1, inplace=True)
    
    result.loc[:, "url"] = 'https://twitter.com/' + \
        result.user.astype(str) + '/status/' + \
        result.fid.astype(str)
    
    result.loc[:, "keyword"] = keyword if keyword else 'nan'

    # Delete unwanted columns
    drop_cols = obj_to_lst(drop_cols)

    if drop_cols:
        result.drop(drop_cols, axis=1, inplace=True)
    
    return result


def search_places(_lat, lng, radius):
    """
    Search Places using API Twitter
    """
    
    import tweepy
    
    # Give our credentials to the Twitter API
    auth = tweepy.OAuthHandler(
        TWITTER_TOKEN['CONSUMER_KEY'], TWITTER_TOKEN['CONSUMER_SECRET']
    )

    auth.set_access_token(
        TWITTER_TOKEN['TOKEN'], TWITTER_TOKEN['SECRET']
    )

    api = tweepy.API(auth_handler=auth)
    
    # Reqest data from twitter
    data = api.reverse_geocode(lat=_lat, long=lng,
        accuracy=radius
    )
    
    return data


def geotweets_location(inGeom, epsg_in, keyword=None, epsg_out=4326,
                       onlySearchAreaContained=True, keyToUse=None):
    """
    Search data in Twitter and array with that data
    
    inGeom cloud be a shapefile with a single buffer feature or a dict like:
    inGeom = {
        x: x_value,
        y: y_value,
        r: dist (in meters)
    }
    or a list or a tuple:
    inGeom = [x, y, radius]
    """
    
    from shapely.geometry     import Polygon, Point
    from geopandas            import GeoDataFrame
    from glass.prop.feat.bf import getBufferParam
    
    x_center, y_center, dist = getBufferParam(inGeom, epsg_in, outSRS=4326)
    
    # Extract data from Twitter
    data = search_tweets(
        lat=y_center, lng=x_center, radius=float(dist) / 1000,
        keyword=keyword, NR_ITEMS=500, only_geo=True, key=keyToUse
    )
    
    try:
        if not data:
            return 0
    except:
        pass
    
    # Pandas to GeoPandas
    geoms = [Point(xy) for xy in zip(data.longitude, data.latitude)]
    data.drop(["latitude", "longitude"], axis=1, inplace=True)
    gdata = GeoDataFrame(data, crs='EPSG:4326', geometry=geoms)
    
    if onlySearchAreaContained:
        from shapely.wkt               import loads
        from glass.prj.obj           import prj_ogrgeom
        from glass.gp.prox.bfing.obj import xy_to_buffer
        
        # Check if all retrieve points are within the search area
        _x_center, _y_center, _dist = getBufferParam(
            inGeom, epsg_in, outSRS=3857)
        
        search_area = xy_to_buffer(
            float(_x_center), float(_y_center), float(_dist)
        )
        search_area = prj_ogrgeom(search_area, 3857, 4326)
        search_area = loads(search_area.ExportToWkt())
        
        gdata["tst_geom"] = gdata["geometry"].intersects(search_area)
        gdata = gdata[gdata["tst_geom"] == True]
        
        gdata.reset_index(drop=True, inplace=True)
    
    gdata.drop("tst_geom", axis=1, inplace=True)
    
    if epsg_out != 4326:
        gdata = gdata.to_crs(f'EPSG:{str(epsg_out)}')
    
    return gdata


def tweets_to_shp(buffer_shp, epsg_in, outshp, keyword=None,
                  epsg_out=4326, __encoding__='plain_str', keyAPI=None):
    """
    Search data in Twitter and create a vectorial file with that data
    """
    
    from glass.wt.shp import df_to_shp
    
    tweets = geotweets_location(
        buffer_shp, epsg_in, keyword=keyword,
        epsg_out=epsg_out, keyToUse=keyAPI,
        onlySearchAreaContained=None
    )
    
    try:
        if not tweets:
            return 0
    except:
        pass
    
    df_to_shp(tweets, outshp)
    
    return outshp


def tweets_to_xls(outxls, searchword=None, searchGeom=None, srs=None, lng='pt',
                  NTW=1000, twType='mixed', Key=None):
    """
    Search for Tweets and Export them to XLS
    """
    
    from glass.wt import obj_to_tbl
    
    data = search_tweets(
        keyword=searchword, in_geom=searchGeom, epsg=srs,
        __lang=lng, NR_ITEMS=NTW, resultType=twType, key=Key
    )
    
    try:
        if not data:
            return 0
    except:
        pass
    
    obj_to_tbl(data, outxls, sheetsName='twitter')
    
    return outxls

