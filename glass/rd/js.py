"""
Read JSON data
"""


import json


def json_to_obj(j):
    """
    JSON object
    """

    o = json.load(open(j, 'r'))

    return o

