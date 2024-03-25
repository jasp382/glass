"""
Interect with Sun declination/ascension endpoints
"""

import requests as rq
import json as js

from glass.firecons.rest import rest_params


def get_sun_decl_as(headers, datehour=None, endtime=None):
    """
    Retrieve Sun declination/ascension data
    """

    prm = rest_params()

    p, d, _p = prm["PROTOCOL"], prm["DOMAIN"], prm["PORT"]

    qp = '' if not datehour and not endtime else f"?datetime={str(datehour)}" \
        if datehour and not endtime else \
            f"?startime={str(datehour)}&endtime={str(endtime)}" \
                if datehour and endtime else ''

    url = f'{p}://{d}:{_p}/floc/sun-declination/{qp}'

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
                "json"   : data,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http" : r.status_code
            }
        
    return out


def add_sun_decl_asc(headers, data):
    """
    Add Sun declination/ascension data
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/floc/sun-declination/'

    out = None

    try:
        r = rq.post(url, headers=headers, data=js.dumps(data))
    
    except:
        out = {"status" : -1}
    
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
                "http"   : r.status_code
            }
    
    return out

