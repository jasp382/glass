"""
Constants related with Sentinel data
"""

def con_datahub():
    """
    Return User and password for sentinel data hub
    """

    import json, os

    jsond = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sentinel.json'
    ), 'r'))

    return jsond

