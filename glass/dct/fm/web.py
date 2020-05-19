"""
From Web to Python Objects
"""


def http_to_json(url):
    """
    Return a json object with the json data available in a URL
    """
    
    import urllib3; import json
    
    http = urllib3.PoolManager()
    resp = http.request('GET', url)
    
    js = json.loads(resp.data.decode('utf-8'))
    
    return js


def data_from_get(url, getParams=None, auth=None):
    """
    Return json from URL - GEST Request
    """
    
    import json
    import requests
    
    response = requests.get(
        url=url, params=getParams,
        headers={'content-type' : 'application/json'},
        auth=auth
    )
    
    return json.loads(response.text)


def data_from_post(url, postdata, head='application/json',
    credentials=None):
    """
    Return data retrieve by a POST Request
    """
    
    import json
    import requests
    
    r = requests.post(
        url, data=json.dumps(postdata),
        headers={'content-type' : head},
        auth=credentials
    )
    
    return r.json()
