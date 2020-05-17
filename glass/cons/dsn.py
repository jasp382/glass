"""
Get DSN API keys
"""

def tw_key(allkeys=True):
    """
    Return Twitter Keys
    """

    import json, os

    keys = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'api-keys.json'
    ), 'r'))

    if allkeys:
        return keys["TWITTER"]
    else:
        return keys["TWITTER"][0]

