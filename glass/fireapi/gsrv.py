"""
Make Requests to GeoServer
"""


import requests as rq
import json as js

from glass.firecons.rest import rest_params


def lstws(headers):
    """
    List Workspace
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geosrv/workspaces/'

    out = None

    try:
        r = rq.get(url, headers=headers)
    except:
        out = {"status" : -1, "json" : None, "http" : None}
    
    if not out:
        try:
            _r = r.json()

            if r.status_code == 200:
                data = _r["data"]
            
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


def lststore(headers, wsname):
    """
    List Stores
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geosrv/{wsname}/stores/'

    out = None

    try:
        r = rq.get(url, headers=headers)
    except:
        out = {"status" : -1, "json" : None, "http" : None}
    
    if not out:
        try:
            _r = r.json()

            if r.status_code == 200:
                data = _r["data"]
            
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


def addws(headers, wsname):
    """
    Add new workspace
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geosrv/workspaces/'

    out = None

    try:
        r = rq.post(url, headers=headers, data=js.dumps({
            'workspace' : wsname
        }))
    
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


def addstore(headers, wsname, source, store, _type):
    """
    Add new store
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geosrv/{wsname}/stores/'

    out = None

    try:
        r = rq.post(url, headers=headers, data=js.dumps({
            'store' : store, 'source' : source,
            "store_type" : _type
        }))
    
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


def lstlyr(headers):
    """
    List Layers
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geosrv/layers/'

    out = None

    try:
        r = rq.get(url, headers=headers)
    
    except:
        out = {"status" : -1, "json" : None, "http" : None}

    if not out:
        try:
            _r = r.json()

            if r.status_code == 200:
                data = _r["data"]
            
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


def addlyr(headers, source, wsname, store, _type):
    """
    Add new Geoserver layer

    store_type options:
    * psql
    * raster
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url, out = f'{p}://{d}:{_p}/geosrv/layers/', None

    try:
        r = rq.post(url, headers=headers, data=js.dumps({
            'source' : source, 'workspace' : wsname,
            'store' : store, "store_type" : _type
        }))
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


def up_lyr_style(headers, lyr, style):
    """
    Update Geoserver layer style
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url, out = f'{p}://{d}:{_p}/geosrv/layer/{lyr}/', None

    try:
        r = rq.put(
            url, headers=headers,
            data=js.dumps({'style' : style})
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


def rmlyr(headers, layer):
    """
    Remove existing GeoServer Layer
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/geosrv/layer/{layer}/'

    r = rq.delete(url, headers=headers)

    return r


def add_style(headers, name):
    """
    Add GeoServer Style
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url, out = f'{p}://{d}:{_p}/geosrv/styles/', None

    try:
        r = rq.post(
            url, headers=headers,
            data=js.dumps({'name' : name})
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


def add_sld(headers, style, d_):
    """
    Add GeoServer Style
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url, out = f'{p}://{d}:{_p}/geosrv/style/{style}/', None

    try:
        r = rq.put(url, headers=headers, data=js.dumps(d_))
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

