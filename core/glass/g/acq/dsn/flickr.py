"""
Methods to extract data from Flickr
"""

# Flickr
FLICKR_PUBLIC = 'b4f00205d43bfe8a4edd40f800388eb3'
FLICKR_SECRET = 'c235398aae0743f0'

def search_photos(lat=None, lng=None, radius=None, keyword=None,
                  apiKey=None):
    """
    Method to connect with Flickr in order to querie photos and other kinds
    of data using keyworkds, coordinates and a radius
    
    Returns a Pandas Dataframe
    """
    
    import pandas
    from flickrapi       import FlickrAPI
    from glass.ng.pd.fld import listval_to_newcols
    
    if apiKey:
        FLIC_PUB, FLIC_SEC = apiKey
    else:
        FLIC_PUB, FLIC_SEC = FLICKR_PUBLIC, FLICKR_SECRET
    
    flickr_engine = FlickrAPI(
        FLIC_PUB, FLIC_SEC, format='parsed-json', store_token=False
    )
    
    extras = 'url_l,geo,date_taken,date_upload,description'
    
    keywords = '' if not keyword else keyword
    
    if not lat or not lng or not radius:
        data = flickr_engine.photos.search(
            text=keyword, pp=500, extras=extras
        )
    
    else:
        data = flickr_engine.photos.search(
            text=keyword, lat=lat, lon=lng, radius=radius, pp=500,
            extras=extras
        )
    
    photos_array = pandas.DataFrame(data['photos']['photo'])
    
    if not photos_array.shape[0]:
        return None
    
    photos_array = listval_to_newcols(photos_array, "description")
    
    return photos_array


def photos_location(buffer_shp, epsg_in, keyword=None, epsg_out=4326,
                    onlySearchAreaContained=True, keyToUse=None):
    """
    Search for data in Flickr and return a array with the same data
    
    buffer_shp cloud be a shapefile with a single buffer feature or a dict
    like:
    buffer_shp = {
        x: x_value,
        y: y_value,
        r: dist (in meters)
    }
    or a list or a tuple:
    buffer_shp = [x, y, radius]
    """
    
    import pandas
    from shapely.geometry          import Polygon, Point
    from shapely.wkt               import loads
    from geopandas                 import GeoDataFrame
    from glass.g.gp.prox.bfing.obj import xy_to_buffer
    from glass.g.prop.feat.bf      import getBufferParam
    from glass.g.prj.obj           import prj_ogrgeom
    
    x_center, y_center, dist = getBufferParam(buffer_shp, epsg_in, outSRS=4326)
    
    # Retrive data from Flickr
    photos = search_photos(
        lat=y_center, lng=x_center, radius=float(dist) / 1000,
        keyword=keyword, apiKey=keyToUse
    )
    
    try:
        if not photos:
            # Return noData
            return 0
    except:
        pass
    
    photos['longitude'] = photos['longitude'].astype(float)
    photos['latitude']  = photos['latitude'].astype(float)
    
    geoms = [Point(xy) for xy in zip(photos.longitude, photos.latitude)]
    gdata = GeoDataFrame(photos, crs='EPSG:4326', geometry=geoms)
    
    if onlySearchAreaContained:
        _x_center, _y_center, _dist = getBufferParam(
            buffer_shp, epsg_in, outSRS=3857)
        # Check if all retrieve points are within the search area
        search_area = xy_to_buffer(
            float(_x_center), float(_y_center), float(_dist))
        search_area = prj_ogrgeom(search_area, 3857, 4326)
        search_area = loads(search_area.ExportToWkt())
        
        gdata["tst_geom"] = gdata["geometry"].intersects(search_area)
        gdata = gdata[gdata["tst_geom"] == True]
        
        gdata.reset_index(drop=True, inplace=True)
    
    gdata["fid"] = gdata["id"]
    
    if "url_l" in gdata.columns.values:
        gdata["url"] = gdata["url_l"]
    else:
        gdata["url"] = 'None'
    
    gdata["description"] = gdata["_content"]
        
    # Drop irrelevant fields
    cols = list(gdata.columns.values)
    delCols = []
    
    for col in cols:
        if col != 'geometry' and  col != 'description' and \
            col != 'fid' and col != 'url' and col != 'datetaken' \
            and col != 'dateupload' and col != 'title':
            delCols.append(col)
        else:
            continue
    
    gdata.drop(delCols, axis=1, inplace=True)
    
    if epsg_out != 4326:
        gdata = gdata.to_crs('EPSG:{}'.format(str(epsg_out)))
    
    return gdata


def photos_to_shp(buffer_shp, epsg_in, outshp, keyword=None,
                  epsg_out=4326, apikey=None, onlyInsideInput=True):
    """
    Search for data in Flickr and return a Shapefile with the 
    data.
    """
    
    from glass.g.wt.shp import df_to_shp
    
    photos = photos_location(
        buffer_shp, epsg_in, keyword=keyword, epsg_out=epsg_out,
        keyToUse=apikey, onlySearchAreaContained=onlyInsideInput
    )
    
    try:
        if not photos: return 0
    except: pass
    
    df_to_shp(photos, outshp)
    
    return outshp

