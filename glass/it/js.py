"""
Data to JSON Files
"""

import pandas as pd


def xls_to_json(xls, jsf, sheet=None):
    """
    XLSx to JSON 
    """

    from glass.rd import tbl_to_obj
    from glass.wt.js import dict_to_json

    df = tbl_to_obj(xls, sheet=sheet)

    d = df.to_dict()

    dict_to_json(d, jsf)

    return jsf


def json_to_xls(jsf, xls, sheet=None):
    """
    JSON to XLSx
    """

    from glass.wt import obj_to_tbl

    df = pd.read_json(jsf, orient='records')

    obj_to_tbl(
        df, xls,
        sheetsName='data' if not sheet else sheet
    )

    return xls
