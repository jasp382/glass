"""
Get DSN API keys
"""

import json, os

def tw_key(allkeys=True):
    """
    Return Twitter Keys
    """

    keys = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'api-keys.json'
    ), 'r'))

    if allkeys:
        return keys["TWITTER"]
    else:
        return keys["TWITTER"][0]


def search_words(group=None):
    """
    Get Search Words
    """

    from glass.pys      import obj_to_lst
    from glass.ng.sql.q import q_to_obj

    db = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'ecgiwords.db'
    )

    group = obj_to_lst(group)

    Q = "SELECT words.fid, words.word FROM words ORDER BY words.fid" if not group else (
        "SELECT words.fid, words.word FROM words "
        "INNER JOIN groups ON words.grpid = groups.fid "
        "WHERE {} "
        "ORDER BY words.fid"
    ).format(" OR ".join(["groups.design = '{}'".format(x) for x in group]))

    words = q_to_obj(db, Q, db_api='sqlite')

    return words

