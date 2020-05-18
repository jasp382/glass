"""
Uses for Search Endpoint of the Facebook Graph API
"""

from . import FACEBOOK_GRAPH_URL
from . import FACEBOOK_TOKEN


def by_query(search_type,
                    keyword=None, x_center=None, y_center=None, dist=None,
                    limit='100', face_fields=None):
    """
    Search data on facebook based on:
    - Keyword;
    - search type (user, page, event, place, placetopic);
    - location (center and distance from center);
    - limit (maximum number of users/pages/etc. to be returned)*.
    
    * Our default is 100, but the Facebook default is 60.
    
    Returns an array with the id of the data in facebook
    """
    
    import pandas
    from glass.pyt    import obj_to_lst
    from glass.fm.web import http_to_json
    
    # Deal with spaces in the keyword expression and with special characters
    keyword = keyword.replace(' ', '%20') if keyword and ' ' in keyword \
        else keyword
    
    face_fields = obj_to_lst(face_fields)

    URL = (
        '{graph}search?access_token={_id}|{scrt}'
        '{_q}{typ}{cnt}{dst}{lmt}{flds}'
    ).format(
        graph=FACEBOOK_GRAPH_URL,
        _id  = FACEBOOK_TOKEN['APP_ID'],
        scrt = FACEBOOK_TOKEN['APP_SECRET'],
        _q   = '' if not keyword else '&q={}'.format(keyword),
        typ  = '&type={}'.format(search_type),
        cnt  = '' if not x_center and not y_center else '&center={},{}'.format(
            y_center, x_center
        ),
        dst  = '' if not dist else '&distance={}'.format(dist),
        lmt  = '' if not limit else '&limit={}'.format(str(limit)),
        flds = '' if not face_fields else '&fields={}'.format(','.join(face_fields))
    )
    
    face_table = pandas.DataFrame(http_to_json(URL)['data'])
    
    if not face_table.shape[0]:
        return None
    
    face_table["url"] = "https://facebook.com//" + face_table["id"]
    
    if face_fields:
        if "location" in face_fields:
            face_table = pandas.concat([
                face_table.drop(["location"], axis=1),
                face_table["location"].apply(pandas.Series)
            ], axis=1)
    
    return face_table

