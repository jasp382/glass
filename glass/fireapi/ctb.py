"""
Manage Contributions
"""

import requests as rq
import json as js

from glass.firecons.rest import rest_params
from glass.pys.web   import get_file


def get_ctb(headers, userid=None, epsg=None,
    geom=None, ugeom=None, geombf=None, geomc_isna=None,
    place_isna=None, stime=None, etime=None, photostatus=None,
    strips=None):
    """
    Return User contributions
    """

    epsg = '3763' if not epsg else str(epsg)

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    geomcisna = "true" if geomc_isna == True else "false" \
        if geomc_isna == False else ""
    
    placeisna = "true" if place_isna == True else "false" \
        if place_isna == False else ""

    url = (
        f'{p}://{d}:{_p}/volu/contributions/?epsg={epsg}'
        '&geomc=true&geombfc=true'
        f'{"" if not geom else "&geom=true"}'
        f'{"" if not ugeom else "&usergeom=true"}'
        f'{"" if not geombf else "&geombf=true"}'
        f'{"" if not userid else "&userid=" + str(userid)}'
        f'{"" if not geomcisna != "" else "&geomcisna=" + geomcisna}'
        f'{"" if not placeisna != "" else "&placeisna=" + placeisna}'
        f'{"" if not stime else f"&starttime={stime}"}'
        f'{"" if not etime else f"&endtime={etime}"}'
        f'{"" if strips == None else f"&strips={str(strips)}"}'
        f'{"" if photostatus == None else f"&photostatus={str(photostatus)}"}'
    )

    out = None

    try:
        r = rq.get(url, headers=headers)
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


def add_contrib(headers, data):
    """
    Add Contributions Data
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/volu/contributions/'

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
                "http" : r.status_code
            }
    
    return out


def update_ctb(h, ctbid, dd):
    """
    Update Dataset
    """

    pp = rest_params()
    p, d, _p = pp["PROTOCOL"], pp["DOMAIN"], pp["PORT"]

    url = f'{p}://{d}:{_p}/volu/contribution/{str(ctbid)}/'

    out = None

    try:
        r = rq.put(url, headers=h, data=js.dumps(dd))
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


def get_onectb(headers, fid, geom=None, geombf=None, epsg=None):
    """
    Return Single Contribution
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url, out = (
        f'{p}://{d}:{_p}/volu/contribution/{str(fid)}/?'
        f'geom={"false" if not geom else "true"}&'
        f'geombf={"false" if not geombf else "true"}'
        f'{"" if not epsg else f"epsg={str(epsg)}"}'
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


def download_ctbphoto(token, picname, out):
    """
    Download contribution photo
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/volu/photo-download/{picname}/'

    try:
        photo, http = get_file(url, out, token=token)

        out = {"photo" : photo, "http" : http, "status" : 1}

    except:
        out = {"photo" : None, "http" : None, "status" : -1}

    return out



def up_ctbazimute(h, ctbid, geom, pid, dd):
    """
    Update Contribution Azimute
    """

    pp = rest_params()
    p, d, _p = pp["PROTOCOL"], pp["DOMAIN"], pp["PORT"]

    url = (
        f'{p}://{d}:{_p}/volu/ctb-azimute/'
        f'{str(ctbid)}/{str(geom)}/{str(pid)}/'
    )

    out = None

    try:
        r = rq.put(url, headers=h, data=js.dumps(dd))
    except:
        out = {"status" : -1}
    
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
                "http"   : r.status_code
            }
    
    return out


def get_ctb_with_places(h):
    """
    Get Places for contributions without that information
    """


    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url = f'{p}://{d}:{_p}/volu/ctb-places/'

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


def get_ctbrst(token, ctbfid, outrst):
    """
    Get Contribution Raster
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/volu/fx-download/{str(ctbfid)}/'

    try:
        rst, http = get_file(url, outrst, token=token)
        out = {
            "raster" : rst,
            "status" : 1,
            "http"   : http
        }
    
    except:
        out = {"status" : -1, "http" : 500}
    
    return out


def add_ctbrst(token, ctb, rst):
    """
    Add Contribution raster
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f"{p}://{d}:{_p}/volu/ctb-fx/{ctb}/"

    out = None

    try:
        with open(rst, 'rb') as f:
            r = rq.post(
                url, files={'fxrst' : f},
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



def ctb_intersections(headers, step):
    """
    Return Contributions Intersections
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url = f'{p}://{d}:{_p}/volu/ctb-i-ctb/{str(step)}/'

    out = None

    try:
        r = rq.get(url, headers=headers)
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


def ctb_groups_valid(headers, ctbs):
    """
    Validate groups and return new groups if 
    necessary
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    _ctbs = [str(c) for c in ctbs]

    qp = f'?ctbs={",".join(_ctbs)}'

    url = f'{p}://{d}:{_p}/volu/ctb-val/{qp}'

    out = None

    try:
        r = rq.get(url, headers=headers)
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

