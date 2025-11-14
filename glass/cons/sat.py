"""
Constants related with Sentinel data
"""

import json, os

from typing import Optional, Dict, Any

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
STAC_URL = "https://stac.dataspace.copernicus.eu/v1"

def con_datahub():
    """
    Return User and password for sentinel data hub
    """

    jsond = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sentinel.json'
    ), 'r'))

    return jsond


def obtain_token(totp: Optional[str] = None, token_url: str = TOKEN_URL, justToken:bool=True) -> Dict[str, Any]:
    """
    Obtém access_token do Copernicus Data Space (Keycloak) usando Resource Owner Password Credentials.
    Retorna o JSON com os campos: access_token, refresh_token, expires_in, ...
    """

    import requests as rq

    jsond = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'credentials.json'
    ), 'r'))

    user = jsond["COPERNICUS_ECOSYSTEM"]["USER"]
    pswd = jsond["COPERNICUS_ECOSYSTEM"]["PASSWORD"]

    payload = {
        "client_id"  : "cdse-public",
        "grant_type" : "password",
        "username"   : user,
        "password"   : pswd
    }

    if totp:
        payload["totp"] = totp
    
    resp = rq.post(token_url, data=payload, timeout=30)
    resp.raise_for_status()

    rd = resp.json()

    token = rd.get("access_token")

    return token if justToken else rd, resp


def get_ibands(sat='sentinel'):
    return [
        'B02_10m', 'B03_10m', 'B04_10m', 'B08_10m',
        'B05_20m', 'B06_20m', 'B07_20m', 'B8A_20m',
        'B11_20m', 'B12_20m', 'B09_60m', 'B01_60m',
        'AOT_10m', 'SCL_20m'
    ] if sat == 'sentinel' else [
        f"B{str(i+1)}" for i in range(11)
    ] if sat == 'landsat' else []


def get_lwibands():
    return [
        'B02', 'B03', 'B04', 'B08',
        'B05', 'B06', 'B07', 'B8a',
        'B11', 'B12', 'B09', 'B01',
        'AOT', 'SCL'
    ]


def bandsmap():
    return {
        'AOT_10m' : 'AOT', 'SCL_20m' : 'SCL',
        'B02_10m' : 'B02', 'B03_10m' : 'B03',
        'B04_10m' : 'B04', 'B08_10m' : 'B08',
        'B05_20m' : 'B05', 'B06_20m' : 'B06',
        'B07_20m' : 'B07', 'B8A_20m' : 'B8A',
        'B11_20m' : 'B11', 'B12_20m' : 'B12',
        'B09_60m' : 'B09', 'B01_60m' : 'B01'
    }


def bands_to_radtag():
    return {
        'b02' :  'blue', 'b03' : 'green',
        'b04' :   'red', 'b08' :   'nir',
        'b11' : 'swir1', 'b12' : 'swir2' 
    }

def get_sentinel2_assets():
    return [
        "B02", "B03", "B04", "B05",
        "B06", "B07", "B08",
        "B11", "B12", "B09", "B01",
        "SCL"
    ]

