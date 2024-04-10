"""
Tools to manage Layers in Geoserver
"""

import requests as rq
import os

from glass.cons.gsrv import con_gsrv
from glass.prop.prj  import epsg_to_wkt
from glass.pys.Xml   import write_xml_tree


def lst_lyr():
    """
    List all layers in the geoserver
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']

    url = f'{_p}://{h}:{p}/geoserver/rest/layers'

    r = rq.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    layers = r.json()

    return [l['name'] for l in layers['layers']['layer']]


def add_pglyr(tbl, ws, st, epsg, outepsg=None):
    """
    Add new PostGIS layer to GeoServer
    """

    G = con_gsrv()

    # Create XML dict
    lyrtitle = f"Title {tbl}"
    elements = {
        "featureType": {
            "name"      : tbl,
            "title"     : lyrtitle,
            "nativeCRS" : str(epsg_to_wkt(epsg))
        }
    }

    if outepsg:
        elements["featureType"]["srs"] = f"EPSG:{str(outepsg)}"
        elements["featureType"]["projectionPolicy"] = "REPROJECT_TO_DECLARED"
    
    xmlfile = write_xml_tree(elements, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gsrvtmp', f'{tbl}.xml'
    ))

    # Create Geoserver Layer
    url = (
        f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
        f'geoserver/rest/workspaces/{ws}/'
        f'datastores/{st}/featuretypes'
    )

    with open(xmlfile, 'rb') as __xml:
        try:
            r = rq.post(
                url, data=__xml,
                headers={'content-type' : 'text/xml'},
                auth=(G['USER'], G['PASSWORD'])
            )

            return True, r
        
        except:
            return None, None


def pub_rst_lyr(layer, store, ws, epsg_code):
    """
    Publish a Raster layer
    """

    G = con_gsrv()
    
    url = (
        f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
        f'geoserver/rest/workspaces/{ws}/'
        f'coveragestores/{store}/coverages'
    )
    
    # Create obj with data to be written in the xml
    xmlTree = {"coverage" : {
        "name"      : layer,
        "title"     : layer,
        "nativeCRS" : str(epsg_to_wkt(epsg_code)),
        "srs"       : f'EPSG:{str(epsg_code)}'
    }}
    
    # Write XML
    xml_file = write_xml_tree(xmlTree, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gsrvtmp', f'{layer}.xml'
    ))
    
    # Create layer
    with open(xml_file, 'rb') as f:
        try:
            r = rq.post(
                url, data=f,
                headers={'content-type': 'text/xml'},
                auth=(G['USER'], G['PASSWORD'])
            )

            return True, r
        
        except:
            return None, None


def dellyr(lyr):
    """
    Delete Layer
    """

    G = con_gsrv()

    url = (
        f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
        f"geoserver/rest/layers/{lyr}"
    )

    try:
        r = rq.delete(url, auth=(G["USER"], G["PASSWORD"]))

    except:
        r = None
    
    return r

