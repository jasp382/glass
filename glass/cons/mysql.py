"""
Constants for MySQL API
"""

def con_mysql():
    """
    Return Dict to Connect to MySQL
    """

    import json, os

    return json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'con-mysql.json'
    ), 'r'))
