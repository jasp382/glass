"""
GeoServer Constants
"""

def con_gsrv():
    """
    Return Dict to Connect to Geoserver
    """

    import json, os

    return json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'con-geoserver.json'
    ), 'r'))
