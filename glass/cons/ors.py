"""
Open Route Service constants
"""

MAIN_URL = "https://api.openrouteservice.org/v2/"

ISOCHRONES_URL = 'https://api.openrouteservice.org/v2/isochrones/'


def ors_token():
    """
    Return Open Route Service Token
    """

    import json, os

    d = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'open-route-service.json'
    ), 'r'))

    return d["ORS"]

