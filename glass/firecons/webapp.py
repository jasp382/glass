"""
Conection to fireloc web application
"""


def con_webapp():
    import json as js
    import os

    cp = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'client-app.json'
    ), 'r'))

    return cp

