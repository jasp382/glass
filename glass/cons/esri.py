"""
Constants for using ESRI services
"""

"""GLOBAL VARIABLES"""

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

TV_URL = (
    "https://route.arcgis.com/arcgis/rest/services/World/ServiceAreas"
    "/NAServer/ServiceArea_World/retrieveTravelModes?"
)

"""
Tokens
"""

def rest_token():
    """
    Return token for using ArcGIS Rest Services
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

def get_tvmodes():
    """
    Return travel modes
    """

    import requests as rqsts
    from glass.cons.esri import TV_URL, rest_token

    token = rest_token()

    tvs = rqsts.get(TV_URL, params={'f' : 'json', 'token' : token})

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
    """

    import requests as rqsts
    from glass.cons.esri import TV_URL, rest_token

    token = rest_token()

    tvs = rqsts.get(TV_URL, params={'f' : 'json', 'token' : token})

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

