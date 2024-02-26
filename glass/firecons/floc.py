"""
Constants related with Fire location identification
"""

def floc_param():
    """
    Return Fire Loc parameters
    """

    import json as js
    import os

    fp = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'floc.json'
    ), 'r'))

    return fp

