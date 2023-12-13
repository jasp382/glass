"""
Fire location identification endpoints
"""


import requests as rq
import json as js

from glass.firecons.rest import rest_params


def get_floc(h, step=None, ictb=None, geom=None, ext=None, epsg=None):
    """
    Return Fire identified by the system
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    show_ctb = "true" if ictb == True else "false" \
        if ictb == False else "false"
    
    url, out = (
        f'{p}://{d}:{_p}/floc/fireloc/?'
        f'geom={"false" if not geom else "true"}&'
        f'extent={"false" if not ext else "true"}&'
        f'contribs={show_ctb}'
        f'{"" if step == None else f"&step={str(step)}"}'
        f'{"" if not epsg else f"&epsg={str(epsg)}"}'
    ), None

    try:
        r = rq.get(url, headers=h)
    except:
        out = {"status" : -1, "json" : None, "http" : None}
    
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
                "json"   : None,
                "http"   : r.status_code
            }
    
    return out


def get_onefloc(headers, fid, ictb, geom=None, ext=None, epsg=None):
    """
    Return Single Contribution
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    show_ctb = "true" if ictb == True else "false" \
        if ictb == False else "false"

    url, out = (
        f'{p}://{d}:{_p}/floc/fireloc-i/{str(fid)}/?'
        f'geom={"false" if not geom else "true"}&'
        f'extent={"false" if not ext else "true"}&'
        f'contribs={show_ctb}'
        f'{"" if not epsg else f"&epsg={str(epsg)}"}'
    ), None

    try:
        r = rq.get(url, headers=headers)
    except:
        out = {"status" : -1, "json" : None, "http" : None}
    
    if not out:
        try:
            _r = r.json()

            out = {
                "status" : 1,
                "json"   : _r,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http"   : r.status_code
            }
    
    return out


def add_floc(headers, data):
    """
    Add System event detection results
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/floc/fireloc/'

    out = None
    
    try: 
        r = rq.post(url, headers=headers, data=js.dumps(data))
        
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


def up_floc(headers, flocid, data):
    """
    Update Fire located
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/floc/fireloc-i/{flocid}/'

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


def floc_ctb(token, flocid, ctbs):
    """
    Relate Fire event with contributions
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/floc/floc-ctbs/{str(flocid)}/'

    out = None

    try: 
        r = rq.put(
            url, headers=token,
            data=js.dumps({"ctbs" : ctbs})
        )
        
    except Exception as e:
        print(e)
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


def add_flocrst(token, floclyr, rst):
    """
    Add Fire Location raster
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f"{p}://{d}:{_p}/floc/floc-raster/{floclyr}/"

    out = None

    try:
        with open(rst, 'rb') as f:
            r = rq.post(
                url, files={'flocraster' : f},
                headers={'Authorization' : token['Authorization']}
            )
    except:
        out = {"status" : -1, "json" : None, "http" : None}
    
    if not out:
        try:
            _r = r.json()

            out = {
                "status" : 1,
                "json"   : _r,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http"   : r.status_code
            }
    
    return out


def get_floc_places(h):
    """
    Get Places for fire locations without that information
    """


    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url = f'{p}://{d}:{_p}/floc/floc-places/'

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


def get_floc_near_floc(h, cstep, fstep):
    """
    Get Old Firelocs near New Firelocs
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    qp  = f"?cstep={cstep}&fstep={fstep}"
    url = f'{p}://{d}:{_p}/floc/floc-near-floc/{qp}'

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

