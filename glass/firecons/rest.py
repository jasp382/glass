"""
FIREAPI REST API connection parameters
"""


def rest_params():
    """
    Return all necessary data to make requests
    to the FIREAPI REST API
    """

    import json, os

    v = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'rest.json'
    ), 'r'))

    return v