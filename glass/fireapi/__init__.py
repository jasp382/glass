"""
Tools to retrieve information from the FIRE REST API
"""

import requests as rq
import json     as js

from glass.firecons.rest import rest_params


def get_headers():
    """
    Return HEADERS with authentication token
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url_token = f"{p}://{d}:{_p}/auth/token/new/"

    headers = {
        'content-type'  : 'application/json',
    }

    data = {
        "userid"   : params["SUPER"],
        "password" : params["PASSWORD"]
    }

    out = None
    
    try:
        r = rq.post(url_token, headers=headers, data=js.dumps(data))
    except:
        out = {"status" : -1, "http" : None, "json" : None}
    
    if not out:
        try:
            _r = r.json()

            if r.status_code == 201:
                token = f'{_r["token_type"]} {_r["access_token"]}'
                headers["Authorization"] = token

                data = headers
            else:
                data = _r
            
            out = {
                "status" : 1,
                "json"   : data,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http"   : r.status_code
            }
    
    return out

