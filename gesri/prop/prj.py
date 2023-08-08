"""
PRJ
"""

def get_wkt_esri(epsg):
    import requests
    
    URL = "https://epsg.io/{}.esriwkt".format(epsg)
    
    r = requests.get(URL)
    
    return str(r.text)

