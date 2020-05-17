"""
Open Route Service constants
"""

MAIN_URL = "https://api.openrouteservice.org/v2/"


def get_ors_token():
    """
    Return Open Route Service Token
    """

    import json, os

    d = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'api-keys.json'
    ), 'r'))

    return d["OPEN_ROUTE_SERVICE"]

