"""
Darknet related
"""


def darkpath():
    """
    Return path to darknet
    """

    import json as js
    import os

    cp = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'photo-class.json'
    ), 'r'))

    return cp["DARKNET"]


def photocls_param():
    """
    Return Parameters related with the
    photo classifications
    """

    import json as js
    import os

    cp = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'photo-class.json'
    ), 'r'))

    return cp

