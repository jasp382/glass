"""
Photo Classification related
"""


import requests as rq
import json as js

from glass.firecons.rest import rest_params


def get_photoattrs(h):
    """
    Return Photos Classification Attributes
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url = f"{p}://{d}:{_p}/floc/photocls-attrs/"

    r = rq.get(url, headers=h)

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
            out = {
                "status" : 0,
                "http"   : r.status_code
            }
    
    return out



def add_photoattr(h, attr):
    """
    Add Photo Attribute
    """

    rp = rest_params()
    p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]

    url = f"{p}://{d}:{_p}/floc/photocls-attrs/"

    out = None

    try:
        r = rq.post(url, headers=h, data=js.dumps(attr))
    
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



# -------------------------------------- #
# -------------- Procedures ------------ #

def get_photoprcd(h, stepone=None, steptwo=None, stepthree=None, stepfour=None):
    """
    Get Photos Procedures
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    qp = "" if stepone == None and steptwo == None and stepthree == None \
        and stepfour == None else "?{}{}{}{}".format(
            "" if stepone==None else f"stepone={str(stepone)}&",
            "" if steptwo==None else f"steptwo={str(steptwo)}&",
            "" if stepthree==None else f"stepthree={str(stepthree)}&",
            "" if stepfour==None else f"stepfour={str(stepfour)}"
        )

    url = f'{p}://{d}:{_p}/floc/photo-prcds/{qp}'

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
            out = {
                "status" : 0,
                "http"   : r.status_code
            }

    return out


def add_prcd(h, dd):
    """
    Add new photo procedure
    """

    source = 'cmems' if source != 'sentinel' else source

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/prcd/{source}/'

    out = None

    try:
        r = rq.post(url, headers=h, data=js.dumps(dd))
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


def update_prcd(h, source, prid, dd):
    """
    Update existing procedure

    source options:
    * sentinel
    * cmems
    """

    source = 'cmems' if source != 'sentinel' else source

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/prcd/{source}/{str(prid)}/'

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
                "json" : _r,
                "http" : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http" : r.status_code
            }

    return out

# -------------------------------------- #
# -------------------------------------- #

# -------------------------------------- #
# ------ Classification results -------- #

def add_photocls(token, data):
    """
    Add photo classification results
    """

    params = rest_params()
    p, d, _p = params["PROTOCOL"], params["DOMAIN"], params["PORT"]

    url = f'{p}://{d}:{_p}/floc/photos-class/'

    out = None

    try: 
        r = rq.post(url, headers=token, data=js.dumps(data))
        
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

