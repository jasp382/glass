"""
Constants for PostgreSQL Operations
"""


PG_SPECIAL_WORDS = ['table', 'column', 'natural', 'group', 'left', 'right',
                    'order']

def con_psql(db_set='default'):
    """
    Return Dict to Connect to PostgreSQL
    """

    import json, os

    con_param = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'con-postgresql.json'
    ), 'r'))

    db_set = 'default' if db_set == None or \
        db_set not in con_param else db_set

    return con_param[db_set]
