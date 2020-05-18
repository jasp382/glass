"""
Methods to extract data from facebook
"""

# ------------------------------ #
"""
Global Variables
"""
FACEBOOK_GRAPH_URL = "https://graph.facebook.com/"

FACEBOOK_TOKEN = {
    'APP_SECRET': "c45d19b6c7d1d0fa1889d449549192e4",
    'APP_ID': "116607492275076",
    'USER_TOKEN': ('')
}

FACEBOOK_DATA_TYPES = [
    'posts', 'photos', 'videos', 'locations'
]

FACEBOOK_SEARCH_TYPES = [
    'user', 'page', 'event', 'place', 'placetopic'
]

FACEBOOK_NODE_FIELDS = {
    'posts': [
        'id', 'created_time', 'description', 'from', 'link',
        'message', 'message_tags', 'name', 'permalink_url', 'picture',
        'place', 'properties', 'shares', 'source', 'story', 'status_type',
        'story_tags', 'to', 'type', 'updated_time', 'with_tags'
        #'admin_creator', 'application', 'call_to_action', 'caption',
        #'feed_targeting, 'icon', 'instagram_eligibility', 'privacy',
        #'promotable_id', 'promotion_status'
    ]
}
# ------------------------------ #


def get_location(facebook_id):
    """
    Return the absolute location (x, y) of some facebook id
    """
    
    from glass.fm.web import http_to_json
    
    url = '{grph}{__id}?fields=location&access_token={t_id}|{scret}'.format(
        grph=FACEBOOK_GRAPH_URL, __id=str(facebook_id),
        t_id=FACEBOOK_TOKEN['APP_ID'], scret=FACEBOOK_TOKEN['APP_SECRET']
    )
    
    data = http_to_json(url)['location']
    
    return data['longitude'], data['latitude']


def get_all_fields_by_id(facebook_id, data_type):
    """
    Return all data avaiable for a post, photo, video, etc.
    """
    
    from glass.fm.web import http_to_json
    
    url = '{base}{_id_}/?fields={fld}&access_token={t_id}|{scret}'.format(
        base=FACEBOOK_GRAPH_URL, _id_=str(facebook_id),
        fld=','.join(FACEBOOK_NODE_FIELDS[data_type]),
        t_id=FACEBOOK_TOKEN['APP_ID'], scret=FACEBOOK_TOKEN['APP_SECRET']
    )
    
    data = http_to_json(url)
    
    return data


def search_pages_and_retrieve_data(search_words):
    """
    Receive a keyword and use it to search for pages with a similar name.
    
    In the finded pages, this method will compile a array with all kinds
    of data in that pages. The compiled data could be filter if we define
    several words to filter data.
    """
    
    # Search for pages
    fb_pages = search_by_query('page', search_words)
    
    # Retrive data from each page
    for page in fb_pages:
        page['posts'] = extract_by_page(str(page['id']), 'posts')
        for post in page['posts']:
            post['data'] = get_all_fields_by_id(str(post['id']), 'posts')
        
        page['photos'] = extract_by_page(str(page['id']), 'photos')
        page['videos'] = extract_by_page(str(page['id']), 'videos')
    
    return fb_pages

