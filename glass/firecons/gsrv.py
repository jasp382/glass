"""
Constants for GeoServer Operations
"""


def con_gsrv():
    """
    Return Dict to Connect to GEOSERVER
    """

    import json as js
    import os

    cp = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'con-geoserver.json'
    ), 'r'))

    return cp

