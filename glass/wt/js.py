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


def df_to_json(df, outjson):
    """
    Write DataFrame in JSON
    """

    df.to_json(
        path_or_buf=outjson,
        orient='records'
    )

    return outjson

