"""
Write json data
"""

import json


def dict_to_json(d, outjson):
    """
    Write dict in JSON
    """

    with open(outjson, 'w') as jf:
        json.dump(d, jf, indent=4)

    return outjson

