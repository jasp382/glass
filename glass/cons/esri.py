"""
Constants for using ESRI services
"""

import requests as rq

"""GLOBAL VARIABLES"""

R_URL = (
    "https://route-api.arcgis.com/arcgis/rest/services/"
    "World/Route/NAServer/Route_World/solve?"
)

SA_URL = (
    'https://route.arcgis.com/arcgis/rest/services'
    '/World/ServiceAreas/NAServer/ServiceArea_World/'
    'solveServiceArea?'
)

CF_URL = (
    'https://route.arcgis.com/arcgis/rest/services/World/'
    'ClosestFacility/NAServer/ClosestFacility_World/'
    'solveClosestFacility?'
)

"""TV_URL = (
    "https://route.arcgis.com/arcgis/rest/services/World/ServiceAreas"
    "/NAServer/ServiceArea_World/retrieveTravelModes?"
)"""

TV_URL = (
    "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/"
    "Route_World/retrieveTravelModes?"
)




"""
Tokens
"""

def rest_token():
    """
    Return token for using ArcGIS Rest Services

    - Create new tokens at https://developers.arcgis.com/dashboard/
    """

    import json, os

    data = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'api-esri.json'
    ), 'r'))

    return data["token"]

"""
Travel modes
"""

def tvmodes():
    """
    Return travel models raw data
    """

    token = rest_token()

    tvs = rq.get(TV_URL, params={'f' : 'json', 'token' : token})

    return tvs.json()


def get_tvmodes():
    """
    Return travel modes
    """

    token = rest_token()

    tvs = rq.get(TV_URL, params={'f' : 'json', 'token' : token})

    if tvs.status_code == 200:
        d = tvs.json()
        return d['supportedTravelModes']
    else:
        raise ValueError('Something went wrong with the request!')


def get_tv_by_impedancetype(impedance):
    """
    Return TravelMode for the given impedance

    impedance options:
    * WalkTime
    * TravelTime
    """

    token = rest_token()

    tvs = rq.get(TV_URL, params={'f' : 'json', 'token' : token})

    if tvs.status_code == 200:
        tvdata = tvs.json()

        tmode = None

        for tv in tvdata.get('supportedTravelModes'):
            for r in tv['attributeParameterValues']:
                if r['attributeName'] == impedance:
                    tmode = tv
                    break
            
            if tmode:
                break
        
        return tmode
    
    else:
        raise ValueError('Something went wrong with the request!')

