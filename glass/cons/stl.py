"""
Constants related with Sentinel data
"""

def con_datahub():
    """
    Return User and password for sentinel data hub
    """

    import json, os

    jsond = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'sentinel.json'
    ), 'r'))

    return jsond


def get_ibands():
    return [
        'B02_10m', 'B03_10m', 'B04_10m', 'B08_10m',
        'B05_20m', 'B06_20m', 'B07_20m', 'B8A_20m',
        'B11_20m', 'B12_20m', 'B09_60m', 'B01_60m',
        'AOT_10m', 'SCL_20m'
    ]

def get_lwibands():
    return [
        'b02', 'b03', 'b04', 'b08',
        'b05', 'b06', 'b07', 'b8a',
        'b11', 'b12', 'b09', 'b01',
        'aot', 'scl'
    ]

