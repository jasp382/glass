"""
Interact with GeoVis endpoints
"""

import requests as rq
import json as js

from glass.firecons.rest import rest_params


def add_rfirelyr(headers, data):
    """
    Add Real Fire Layer
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geovis/fire-events-layers/'

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


def get_clusterlyr(headers, del_last_lvl=None):
    """
    Retrieve Cluster Layers
    """

    prm = rest_params()

    p, d, _p = prm["PROTOCOL"], prm["DOMAIN"], prm["PORT"]

    qp = '' if not del_last_lvl else '?del_lastlevel=true'

    url = f'{p}://{d}:{_p}/geovis/cluster-layers/{qp}'

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
                "json" : data,
                "http" : r.status_code
            }

        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http"   : r.status_code
            }

    return out


def add_sctblyr(headers, data):
    """
    Add Single Contribution Layer
    """

    params   = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geovis/single-ctb-layers/'

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
                "json"   : _r,
                "http"   : r.status_code
            }
        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http"   :  r.status_code
            }
    
    return out


def add_floclyr(headers, data):
    """
    Add Fireloc layer
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geovis/fireloc-layers/'

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


def get_permlyr(headers):
    """
    Retrieve Contribution Permanent Layers
    """

    prm = rest_params()

    p, d, _p = prm["PROTOCOL"], prm["DOMAIN"], prm["PORT"]


    url = f'{p}://{d}:{_p}/geovis/marker-layers/'

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


def add_permlayers(headers, data):
    """
    Add Marker Cluster Permanent Layers
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geovis/marker-layers/'

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
                "http"   : r.status_code
            }
    
    return out


def get_genfloclyr(headers, del_last_lvl=None):
    """
    Retrieve General Fireloc Layers
    """

    prm = rest_params()

    p, d, _p = prm["PROTOCOL"], prm["DOMAIN"], prm["PORT"]

    qp = '' if not del_last_lvl else '?del_lastlevel=true'

    url = f'{p}://{d}:{_p}/geovis/general-floclyr/{qp}'

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
                "json" : data,
                "http" : r.status_code
            }

        except:
            out = {
                "status" : 0,
                "json"   : None,
                "http"   : r.status_code
            }

    return out

