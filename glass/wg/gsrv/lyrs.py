"""
Tools for Geoserver layers management
"""

import os
import requests

from glass.cons.gsrv import con_gsrv
from glass.prop.prj  import epsg_to_wkt
from glass.pys.char  import random_str
from glass.pys.Xml   import write_xml_tree
from glass.pys.oss   import mkdir, del_folder



def lst_lyr():
    """
    List all layers in the geoserver
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']

    url = f'{_p}://{h}:{p}/geoserver/rest/layers'

    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    layers = r.json()

    return [l['name'] for l in layers['layers']['layer']]


def pub_pglyr(workspace, store, pg_table, title=None):
    """
    Publish PostGIS table in geoserver
    """

    gs_con = con_gsrv()
    host, port, p = gs_con["HOST"], gs_con['PORT'], gs_con['PROTOCOL']
    
    # Create folder to write xml
    wTmp = mkdir(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), random_str(7)
    ))
    
    # Create obj with data to be written in the xml
    lyr_title = f"Title {pg_table}" if not title else title
    elements = {"featureType": {
        "name"  : pg_table,
        "title" : lyr_title
    }}
    
    # Write the xml
    xml_file = write_xml_tree(
        elements,
        os.path.join(wTmp, f'{pg_table}.xml')
    )
    
    # Create Geoserver Layer
    url = (
        f'{p}://{host}:{port}/geoserver/rest/workspaces/{workspace}/'
        f'datastores/{store}/featuretypes'
    )
    
    with open(xml_file, 'rb') as __xml:
        r = requests.post(
            url, data=__xml, headers={'content-type': 'text/xml'},
            auth=(gs_con['USER'], gs_con['PASSWORD'])
        )
        
        __xml.close()
    
    del_folder(wTmp)
    
    return r


def pub_rst_lyr(layername, datastore, workspace, epsg_code):
    """
    Publish a Raster layer
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = (
        f'{_p}://{h}:{p}/geoserver/rest/workspaces/{workspace}/'
        f'coveragestores/{datastore}/coverages'
    )
    
    # Create obj with data to be written in the xml
    xmlTree = {"coverage" : {
        "name"      : layername,
        "title"     : layername,
        "nativeCRS" : str(epsg_to_wkt(epsg_code)),
        "srs"       : f'EPSG:{str(epsg_code)}',
    }}
    
    # Write XML
    wTmp = mkdir(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        random_str(7)
    )) 
    
    xml_file = write_xml_tree(
        xmlTree, os.path.join(wTmp, 'rst_lyr.xml')
    )
    
    # Create layer
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url, data=f,
            headers={'content-type': 'text/xml'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    del_folder(wTmp)
    
    return r


def del_lyr(lyr):
    """
    Delete some layer
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = f'{_p}://{h}:{p}/geoserver/rest/layers/{lyr}'
    
    r = requests.delete(url, auth=(conf["USER"], conf["PASSWORD"]))
    
    return r

