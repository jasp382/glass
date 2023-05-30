"""
Geoapify constants
"""

MAIN_URL = 'https://api.geoapify.com/v1/'

def get_gafy_token():
    """
    Return GeoApiFy Token
    """

    import json, os

    d = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'api-keys.json'
    ), 'r'))

    return d["GEOAPIFY"]

