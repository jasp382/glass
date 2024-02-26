"""
Constants for operations with e-mails
"""

def con_email():
    """
    Return Dict with E-MAIL Settings
    """

    import json as js
    import os

    cp = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'con-email.json'
    ), 'r'))

    return cp

