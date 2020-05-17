"""
Extraction and dealing with Facebook Pages data
"""

from . import FACEBOOK_GRAPH_URL
from . import FACEBOOK_TOKEN


def sanitizeData(df, FACE_PAGE=None):
    from glass.pyt.df.fld import listval_to_newcols
    
    if FACE_PAGE:
        df['page_ref'] = FACE_PAGE
    # Sanitize created_time
    COLS = df.columns.values
        
    if 'created_time' in COLS:
        df['datahora'] = df.created_time.str.replace('T', ' ')
        df["datahora"] = df.datahora.str[:-5]
            
        df.drop(['created_time'], axis=1, inplace=True)
        
    # Sanitize ID
    df.rename(columns={'id' : 'post_id'}, inplace=True)
        
    # Sanitize Places
    if 'place' in COLS:
        df = listval_to_newcols(df, 'place')
        df.rename(columns={
            'id' : 'place_id', 'name' : 'place_name', 0 : 'unk1'
        }, inplace=True)
            
        df = listval_to_newcols(df, 'location')
            
        df.rename(columns={0 : 'unk2'}, inplace=True)
            
        df.drop(['unk1', 'unk2'], axis=1, inplace=True)
        
    return df

def extract_by_page(face_page, data_type='posts', nposts=100, returnNext=None,
                    apiKeyToUse=None):
    """
    Extract data from one or several Facebook pages using the 
    Facebook GRAPH API
    
    The data_type could be:
    * Posts
    * Photos
    * Videos
    * Locations
    
    Reference Doc: https://developers.facebook.com/docs/graph-api/reference/v3.1/post
    """
    
    import pandas
    from glass.dct.fm.web import http_to_json
    
    if not apiKeyToUse:
        KEY_ID, KEY_SECRET = FACEBOOK_TOKEN['APP_ID'], FACEBOOK_TOKEN['APP_SECRET']
    
    else:
        KEY_ID, KEY_SECRET = apiKeyToUse
    
    FIELDS = [
        'message', 'story', 'created_time', 'description', 'full_picture',
        'link', 'place', 'type'
    ] if data_type == 'posts' else None
    
    URL = (
        '{graph}{page}/{dt}/?key=value&access_token={_id}|{secret}'
        '&limit=100{flds}'
    ).format(
        graph  = FACEBOOK_GRAPH_URL,
        page   = face_page,
        _id    = KEY_ID,
        secret = KEY_SECRET,
        dt     = data_type,
        flds   = '' if not FIELDS else '&fields={}'.format(",".join(FIELDS))
    )
    
    try:
        raw_data = http_to_json(URL)
    except:
        print(URL)
        return None, None
    
    data = pandas.DataFrame(raw_data["data"])
    
    if nposts <= 100:
        if not returnNext:
            return sanitizeData(data, FACE_PAGE=face_page)
        
        else:
            if 'paging' in raw_data:
                if 'next' in raw_data['paging']:
                    return sanitizeData(data, FACE_PAGE=face_page), raw_data["paging"]["next"]
                
                else:
                    return sanitizeData(data, FACE_PAGE=face_page), None
            
            else:
                return sanitizeData(data, FACE_PAGE=face_page), None
    
    else:
        N = int(round(nposts / 100.0, 0))
        
        new_URL = raw_data["paging"]["next"]
        for n in range(N-1):
            try:
                moreRawData = http_to_json(new_URL)
            except:
                return None, None
            
            data = data.append(
                pandas.DataFrame(moreRawData['data']), ignore_index=True)
            
            if 'paging' in moreRawData:
                if 'next' in moreRawData['paging']:
                    new_URL = moreRawData["paging"]["next"]
                else:
                    break
            else:
                break
        
        if not returnNext:
            return sanitizeData(data, FACE_PAGE=face_page)
        
        else:
            return sanitizeData(data, FACE_PAGE=face_page), new_URL


def extract_from_url_and_next(url, Nnext=None, returnNext=None):
    """
    Extract data from Facebook URL and from next URL's until fullfil Nnext
    """
    
    import pandas
    from glass.dct.fm.web import http_to_json
    
    raw_data = http_to_json(url)
    
    data = pandas.DataFrame(raw_data["data"])
    
    if not Nnext:
        if not returnNext:
            return sanitizeData(data)
        
        else:
            if 'paging' in raw_data:
                if 'next' in raw_data['paging']:
                    return sanitizeData(data, raw_data["paging"]["next"])
                else:
                    return sanitizeData(data, None)
            
            else:
                return sanitizeData(data, None)
    
    else:
        if 'paging' not in raw_data:
            if not returnNext:
                return sanitizeData(data)
            
            else:
                return data, None
        
        if 'next' not in raw_data['paging']:
            if not returnNext:
                return data
            
            else:
                return data, None
        
        for i in range(Nnext):
            new_URL = raw_data["paging"]["next"]
            
            moreRawData = http_to_json(new_URL)
            
            data = data.append(
                pandas.DataFrame(moreRawData['data']), ignore_index=True
            )
            
            if 'paging' in moreRawData:
                if 'next' in moreRawData['paging']:
                    new_URL = moreRawData['paging']['next']
                else:
                    break
            
            else:
                break
        
        if not returnNext:
            return sanitizeData(data)
        
        else:
            return sanitizeData(data), new_URL

