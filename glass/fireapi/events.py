"""
Interect with Events endpoints
"""

import requests as rq
import json as js

from glass.firecons.rest import rest_params


def get_events(headers, rgeom=None, epsg=None):
    """
    Retrieve Sun declination/ascension data
    """

    prm = rest_params()

    p, d, _p = prm["PROTOCOL"], prm["DOMAIN"], prm["PORT"]

    rg = "true" if rgeom else "false"

    url = (
        f'{p}://{d}:{_p}/events/real-fires/?rgeom={rg}'
        f'{"" if not epsg else f"&epsg={str(epsg)}"}'
    )

    out = None

    try:
        r = rq.get(url, headers=headers)
    except:
        out = {"status" : -1}
    
    if not out:
        try:
            _r = r.json()

            data = _r["data"] if r.status_code == 200 else _r

            out = {
                "status" : 1,
                "json" : data,
                "http" : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http" : r.status_code
            }
        
    return out


def get_fire_places(h):
    """
    Get Places for fire locations without that information
    """


    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url = f'{p}://{d}:{_p}/events/fires-places/'

    out = None

    try:
        r = rq.get(url, headers=h)
    except:
        out = {"status" : -1}
    
    if not out:
        try:
            _r = r.json()

            data = _r["data"] if r.status_code == 200 else _r

            out = {
                "status" : 1,
                "json"   : data,
                "http"   : r.status_code
            }
        
        except:
            out = {"status" : 0, "http" : r.status_code}
    
    return out


def up_fire(headers, _id, data):
    """
    Update Fire located
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/event/real-fire/{_id}/'

    out = None
    
    try: 
        r = rq.put(url, headers=headers, data=js.dumps(data))
        
    except:
        out = {"status" : -1, "json" : None, "http" : None}
    
    if not out:
        try:
            _r = r.json()

            out = {
                "status" : 1,
                "json" : _r,
                "http" : r.status_code
            }
        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http" :  r.status_code
            }
    
    return out

