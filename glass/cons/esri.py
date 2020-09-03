"""
Constants for using ESRI services
"""

"""GLOBAL VARIABLES"""

SA_URL = (
    'https://route.arcgis.com/arcgis/rest/services'
    '/World/ServiceAreas/NAServer/ServiceArea_World/'
    'solveServiceArea?'
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