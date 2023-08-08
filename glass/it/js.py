"""
Data to JSON Files
"""



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

