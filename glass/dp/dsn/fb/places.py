"""
Querying by location and extract data location
"""


def places_by_query(bfShp, epsgIn, keyword=None, epsgOut=4326,
                    _limit='100', onlySearchAreaContained=True):
    """
    Get absolute location of facebook data using the Facebook API and
    Pandas to validate data.
    
    Works only for the 'places' search type
    
    buffer_shp cloud be a shapefile with a single buffer feature
    or a dict like:
    buffer_shp = {
        x: x_value,
        y: y_value,
        r: dist
    }
    
    or a list or a tuple:
    buffer_shp = [x, y, r]
    """
    
    import pandas
    from geopandas                 import GeoDataFrame
    from shapely.geometry          import Polygon, Point
    from glass.geo.gt.prop.feat.bf import getBufferParam
    from glass.dp.dsn.fb.search    import by_query
    
    search_type = 'place'
    
    x_center, y_center, dist = getBufferParam(bfShp, epsgIn, outSRS=4326)
    
    data = by_query(
        search_type, keyword=keyword,
        x_center=x_center, y_center=y_center, dist=dist,
        limit=_limit, face_fields=[
            "location", "name", "category_list", "about",
            "checkins", "description", "fan_count"
        ]
    )
    
    try:
        if not data:
            # Return NoData
            return 0
    except:
        pass
    
    # Sanitize category_list field
    data = pandas.concat([
        data.drop(["category_list"], axis=1),
        data["category_list"].apply(pandas.Series)
    ], axis=1)
    
    _int_cols = [
        c for c in data.columns.values if type(c) == int
    ]
    __int_cols = {
        x : "col_{}".format(str(x)) for x in _int_cols
    }
    data.rename(columns=__int_cols, inplace=True)
    data.rename(columns={"id" : "id_1", "name" : "name_1"}, inplace=True)
    
    for k in __int_cols:
        data = pandas.concat([
            data.drop([__int_cols[k]], axis=1),
            data[__int_cols[k]].apply(pandas.Series)
        ], axis=1)
        
        data.rename(columns={
            'id' : 'id_' + str(k+2),
            'name' : 'name_' + str(k+2)
        }, inplace=True)
        
        if 0 in list(data.columns.values):
            data.drop([0], axis=1, inplace=True)
    
    # Pandas dataframe to Geopandas Dataframe
    geoms = [Point(xy) for xy in zip(data.longitude, data.latitude)]
    data.drop(["latitude", "longitude"], axis=1, inplace=True)
    gdata = GeoDataFrame(data, crs={'init' : 'epsg:4326'}, geometry=geoms)
    
    if onlySearchAreaContained:
        from shapely.wkt       import loads
        from glass.geo.gm.prj  import prj_ogrgeom
        from glass.geo.gm.gop.prox import xy_to_buffer
        
        # Check if all retrieve points are within the search area
        _x_center, _y_center, _dist = getBufferParam(
            bfShp, epsgIn, outSRS=3857
        )
        
        search_area = xy_to_buffer(
            float(_x_center), float(_y_center), float(_dist)
        )
        search_area = prj_ogrgeom(search_area, 3857, 4326)
        search_area = loads(search_area.ExportToWkt())
        
        gdata["tst_geom"] = gdata["geometry"].intersects(search_area)
        gdata = gdata[gdata["tst_geom"] == True]
        
        gdata.reset_index(drop=True, inplace=True)
    
    # Sanitize id
    gdata["fid"]     = gdata["id_1"]
    gdata["fb_type"] = search_type
    
    __DROP_COLS = ["id_1", "city", "country", "street", "zip", "located_in"]
    DROP_COLS = [c for c in __DROP_COLS if c in gdata.columns.values]
    if onlySearchAreaContained:
        DROP_COLS.append("tst_geom")
    
    gdata.drop(DROP_COLS, axis=1, inplace=True)
    
    if epsgOut != 4326:
        gdata = gdata.to_crs({'init' : 'epsg:{}'.format(str(epsgOut))})
    
    return gdata


def places_to_shp(searchArea, epsgIn, epsgOut, outShp,
                  keyword_=None, onlySearchArea=True):
    """
    Get Locations From Facebook and Write data in a Vetorial
    File
    """
    
    from glass.geo.gt.toshp import df_to_shp
    
    places = places_by_query(
        searchArea, epsgIn, keyword=keyword_, epsgOut=epsgOut,
        onlySearchAreaContained=onlySearchArea
    )
    
    try:
        if not places: return 0
    except:
        pass
    
    df_to_shp(places, outShp)
    
    return outShp

