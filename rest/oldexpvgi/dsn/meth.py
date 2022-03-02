"""
Run methods for views
"""

def query_dsn(rqst_id, geomstr, sources, keyword, user_id):
    """
    Get data from Social Networks
    """
    
    import datetime;             import pandas as pd
    from geoalchemy2             import Geometry, WKTElement
    from django.contrib.gis.geos import GEOSGeometry
    from gasp.gt.anls.prox.bf    import draw_buffer
    from gasp.adv.dsn.fb.places  import places_by_query
    from gasp.adv.dsn.flickr     import photos_location
    from gasp.adv.dsn.tw         import geotweets_location
    from gasp.gt.prj             import proj
    from gasp.sql.c              import alchemy_engine
    from gasp.g.to               import new_pnt
    from api.settings            import MODULES_DOMAIN, DATABASES
    from dsn.models              import rqsts, lyr, searchgeom
    
    # Get search radius
    lat_lng, radius = geomstr.split('pv')
    lat, lng        = lat_lng.split('s')
    lat, lng        = float(lat.replace('d', '.')), float(lng.replace('d', '.'))
    radius          = float(radius.replace('d', '.'))
    xyr             = {'x' : lng, 'y' : lat, 'r' : radius}
    
    search_geom = draw_buffer(proj(
        new_pnt(lng, lat), None, 3857, inEPSG=4326,
        gisApi='OGRGeom'
    ), radius)
    
    # Get datasources
    dataSrc = sources.split('pv')
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    
    # Search places on facebook
    face_data = places_by_query(
        xyr, 4326, keyword=keyword, epsgOut=3857
    ) if 'FACEBOOK' in dataSrc else 0
    
    # Search data on flickr
    flickr_data = photos_location(
        xyr, 4326, keyword=keyword, epsg_out=3857
    ) if 'FLICKR' in dataSrc else 0
    
    # Search data on twitter
    twitter_data = geotweets_location(
        xyr, 4326, keyword=keyword, epsg_out=3857
    ) if 'TWITTER' in dataSrc else 0
    
    # Search data on Youtube
    youtube_data = 0
    
    # Write data about this request in the database
    rqstI = rqsts.objects.create(
        fid=rqst_id, search_keys=keyword,
        start_time=time_a.time(), date=time_a.date(), user_id=int(user_id),
        isfb=1 if 'FACEBOOK' in dataSrc else 0,
        cntfb=face_data.shape[0] if type(face_data) == pd.DataFrame else 0,
        isflickr=1 if 'FLICKR' in dataSrc else 0,
        cntflickr=flickr_data.shape[0] if type(flickr_data) == pd.DataFrame else 0,
        istw=1 if 'TWITTER' in dataSrc else 0,
        cnttw=twitter_data.shape[0] if type(twitter_data) == pd.DataFrame else 0,
        isyoutb=0, cntyoutb=0
    )
    
    # Update Layer Table
    lyr_id = rqst_id+'_0'
    lyrGeomI = lyr.objects.create(
        fid=lyr_id, rqst=rqstI, slug='sgeom',
        name="Search Area Geometry",
        style="boundary",
        url="{}/api/rest/dsn/feat/searchgeom/{}/".format(
            MODULES_DOMAIN, lyr_id
        ),
        dw_url="{}/api/rest/dsn/dw/searchgeom/{}/".format(
            MODULES_DOMAIN, lyr_id
        )
    )
    
    # Update searchgeom table
    sGeomI = searchgeom.objects.create(
        fid=lyr_id+'0', lyr_id=lyrGeomI,
        geom=GEOSGeometry(search_geom.ExportToWkt(), srid=3857)
    )
    
    if type(face_data) == int and type(flickr_data) == int and \
        type(twitter_data) == int and type(youtube_data) == int:
        # It means that there is nodata
        
        rqstI.status = '202'
        rqstI.save()
        
        return '202', rqst_id
    
    extracted_data = {
        'facebook' : face_data,
        'twitter'  : twitter_data,
        'flickr'   : flickr_data,
        'youtube'  : youtube_data
    }
    
    slugD = {'facebook' : 'fb', 'twitter' : 'tw', 'flickr' : 'fckr',
            'youtube' : 'ytb'}
    
    lyrN = {'facebook' : 'Facebook Layer', 'twitter' : 'Twitter Layer',
            'flickr' : 'Flickr Layer', 'youtube' : 'Youtube Layer'}
    
    styles = {
        'facebook' : 'pnt_facebook', 'flickr'   : 'pnt_flickr',
        'twitter'  : 'pnt_twitter', 'youtube'  : 'pnt_youtube'
    }
    
    sqlEngine = alchemy_engine(DATABASES['default'])
    e = 1
    for k in extracted_data:
        if type(extracted_data[k]) == int:
            continue
        else:
            # Update LYR TBL
            lyr_id = rqst_id+'_{}'.format(str(e))
            lyr_i = lyr.objects.create(
                fid=lyr_id, slug=slugD[k], name=lyrN[k], rqst=rqstI,
                style=styles[k], url='{}/api/rest/dsn/feat/{}/{}/'.format(
                    MODULES_DOMAIN, slugD[k], lyr_id
                ),
                dw_url='{}/api/rest/dsn/dw/{}/{}/'.format(
                    MODULES_DOMAIN, slugD[k], lyr_id
                )
            )
            
            # Prepare data to go to the DB
            extracted_data[k]["id"] = lyr_id + extracted_data[k].index.astype(str)
            extracted_data[k]["lyr_id"] = lyr_id
            
            extracted_data[k]["geom"] = extracted_data[k]["geometry"].apply(
                lambda x: WKTElement(x.wkt, srid=3857)
            )
            
            extracted_data[k].drop(["geometry"], axis=1, inplace=True)
            
            # Delete unexpected fields
            if k == 'facebook':
                expCols = [
                    "id", "fid", "cell_id", "lyr_id", "fb_type",
                    "url", "name_1", "about", "description",
                    "fan_count", "checkins", "id_2", "id_3", "id_4",
                    "id_5", "name_2", "name_3", "name_4", "name_5", "geom"
                ]
                
                extracted_data[k]['about'] = extracted_data[k]["about"].str[:499]
                extracted_data[k]['description'] = extracted_data[k]["description".str[:9999]]
            
            elif k == 'twitter':
                expCols = [
                    "id", "fid", "cell_id", "lyr_id", "text",
                    "user", "url", "geom"
                ]
                
                extracted_data[k]["text"] = extracted_data[k]["text"].str[:254]
                extracted_data[k]["user"] = extracted_data[k]["user"].str[:254]
            
            elif k == 'flickr':
                expCols = [
                    "id", "fid", "lyr_id", "owner",
                    "place_id", "title", "name", "datetaken",
                    "description", "dateupload", "url", "geom"
                ]
                
                extracted_data[k]["description"] = extracted_data[k]["description"].str[:9999]
            
            else:
                expCols = []
            
            delCols = []
            for c in list(extracted_data[k].columns.values):
                if c not in expCols:
                    delCols.append(c)
            
            if delCols:
                extracted_data[k].drop(delCols, axis=1, inplace=True)
            
            extracted_data[k].to_sql(
                "dsn_{}".format(k), sqlEngine, if_exists='append', index=False,
                dtype={'geom' : Geometry('POINT', srid=3857)}
            )
            
            e += 1
    
    # Add end time to the requests table
    time_b = datetime.datetime.now().replace(microsecond=0)
    rqstI.end_time = time_b.time()
    rqstI.status = '201'
    rqstI.save()
    
    return 201, rqst_id


def p_query_dsn(RQST, GEOM, SRC, KW, USER_ID):
    """
    Same as query_dsn in production
    """
    
    try:
        STAT, RQST_ID = query_dsn(RQST, GEOM, SRC, KW, USER_ID)
        
        return STAT, RQST_ID
    
    except Exception:
        import sys, traceback, datetime
        from django.contrib.gis.geos import GEOSGeometry
        from gasp.gt.anls.prox.bf    import draw_buffer
        from gasp.gt.prj             import proj
        from gasp.g.to               import new_pnt
        from api.settings            import MODULES_DOMAIN
        from dsn.models              import rqsts, lyr, searchgeom
        
        ERROR_LST = traceback.format_exc().splitlines()
        ERROR_STR = "|".join(ERROR_LST)
        
        # Write ERROR DATA in database
        # - Get Geometry Object
        lat_lng, radius = GEOM.split('pv')
        lat, lng        = lat_lng.split('s')
        lat, lng        = float(lat.replace('d', '.')), float(lng.replace('d', '.'))
        radius          = float(radius.replace('d', '.'))
        
        search_geom = draw_buffer(proj(
            new_pnt(lng, lat), None, 3857, inEPSG=4326, gisApi='OGRGeom'
        ), radius)
        
        # Check if the reques instance was created or not
        rqstIs = rqsts.objects.filter(fid=RQST)
        
        if not len(rqstIs):
            STATUS = '203'
            
            time_a = datetime.datetime.now().replace(microsecond=0)
            rqstI = rqsts.objects.create(
                fid=RQST, search_keys=KW, start_time=time_a.time(),
                date=time_a.date(), user_id=int(USER_ID),
                isfb=1 if 'FACEBOOK' in SRC else 0,
                isflickr=1 if 'FLICKR' in SRC else 0,
                istw=1 if 'TWITTER' in SRC else 0,
                isyoutb=0, cntfb=0, cntflickr=0, cnttw=0, cntyoutb=0,
                end_time=time_a, status=STATUS,
                error=ERROR_STR[:10000]
            )
            
            # Update Layer Table
            lyr_id = RQST + '_0'
            lyrGI = lyr.objects.create(
                fid=lyr_id, rqst=rqstI, slug='sgeom',
                name="Search Area Geometry",
                style="boundary",
                url="{}/api/rest/dsn/feat/searchgeom/{}/".format(
                    MODULES_DOMAIN, lyr_id
                ),
                dw_url="{}/api/rest/dsn/dw/searchgeom/{}/".format(
                    MODULES_DOMAIN, lyr_id
                )
            )
            
            # Update searchgeom table
            sGeomI = searchgeom.objects.create(
                fid=lyr_id+'0', lyr_id=lyrGI,
                geom=GEOSGeometry(search_geom.ExportToWkt(), srid=3857)
            )
        
        else:
            STATUS = '204'
            time_b = datetime.datetime.now().replace(microsecond=0)
            
            rqstI = rqstIs[0]
            rqstI.status = STATUS,
            rqstI.error = ERROR_STR[:10000]
            rqstI.end_time = time_b
            
            rqstI.save()
            
            # Layer Table update is not necessary
        
        return STATUS, RQST

