"""
Interect with GeoRef endpoints
"""

"""
Interect with Sun declination/ascension endpoints
"""

import requests as rq

from glass.firecons.rest import rest_params


def get_ptgeom(headers, rgeom=None, epsg=None):
    """
    Retrieve Sun declination/ascension data
    """

    prm = rest_params()

    p, d, _p = prm["PROTOCOL"], prm["DOMAIN"], prm["PORT"]

    rg = "true" if rgeom else "false"

    url = (
        f'{p}://{d}:{_p}/georef/map-extent/?rgeom={rg}'
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

            out = {
                "status" : 1,
                "json" : _r,
                "http" : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http" : r.status_code
            }
        
    return out
