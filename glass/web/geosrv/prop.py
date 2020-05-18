"""
GeoServer properties
"""

def get_capabilities():
    """
    Get GetCapabilities XML Data
    """

    import os;          import xmltodict
    from glass.to.web    import get_file
    from glass.cons.gsrv import con_gsrv
    from glass.pyt.char  import random_str
    from glass.pyt.oss   import del_file

    conparam = con_gsrv()

    url = (
        "{}://{}:{}/geoserver/wms?request=GetCapabilities"
        "&service=WMS&version=1.1.1"
    ).format(
        conparam["PROTOCOL"], conparam["HOST"], conparam["PORT"]
    )

    xml = get_file(url, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        random_str(10) + '.xml'
    ))

    with open(xml) as xmlf:
        xmld = xmltodict.parse(xmlf.read())
    
    del_file(xml)

    return xmld


def lyrext(work, lyr):
    """
    Return the extent of a Layer in Geoserver
    """

    # Get GetCapabilities Data from GeoServer
    xml_gc = get_capabilities()

    # Get Layer Extent
    lyr_name = "{}:{}".format(work, lyr)
    resp = {}
    lyrs_info = xml_gc['WMT_MS_Capabilities']['Capability']['Layer']['Layer']

    for k in lyrs_info:
        if k['Name'] == lyr_name:
            resp['min_x'] = k['LatLonBoundingBox']['@minx']
            resp['max_x'] = k['LatLonBoundingBox']['@maxx']
            resp['min_y'] = k['LatLonBoundingBox']['@miny']
            resp['max_y'] = k['LatLonBoundingBox']['@maxy']

            break

    return resp
