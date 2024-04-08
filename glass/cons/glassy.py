"""
GLASSY Constants
"""

import json, os

def con_gsrv():
    """
    Return Dict to Connect to Geoserver
    """

    return json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'geoserver-glassy.json'
    ), 'r'))


def con_psql(db_set='default'):
    """
    Return Dict to Connect to PostgreSQL
    """

    con_param = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'psql-glassy.json'
    ), 'r'))

    db_set = 'default' if db_set == None or \
        db_set not in con_param else db_set

    return con_param[db_set]


def rest_params():
    """
    Return all necessary data to make requests
    to the UNDERSEE REST API
    """

    v = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'rest-glassy.json'
    ), 'r'))

    return v

