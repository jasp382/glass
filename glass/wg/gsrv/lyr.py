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

    out = None

    try:
        r = rq.get(
            url, headers={'Accept': 'application/json'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    except Exception as e:
        out = {"status" : -1, "http" : None, "data" : e}

    if not out:
        if r.status_code == 200:
            _l = r.json()

            layers = [l['name'] for l in _l['layers']['layer']]

            out = {
                "status" : 1, "http" : r.status_code,
                "data" : layers
            }
        
        else:
            out = {
                "status" : 0, "http" : r.status_code,
                "data" : r.content
            }
    
    return out


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

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = (
        f'{_p}://{h}:{p}/'
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

    out = None
    
    # Create layer
    try:
        with open(xml_file, 'rb') as f:
            r = rq.post(
                url, data=f,
                headers={'content-type': 'text/xml'},
                auth=(conf['USER'], conf['PASSWORD'])
            )

            out = {"http" : r.status_code}

            if r.status_code == 201:
                out["status"] = 1
                out["data"] = {"layer" : layer}
            
            else:
                out["status"] = 0
                out["data"] = r.content
        
    except Exception as e:
        return {"status" : -1, "http" : None, "data" : e}
    
    return out


def del_lyr(lyr):
    """
    Delete Layer
    """

    G = con_gsrv()

    url = (
        f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
        f"geoserver/rest/layers/{lyr}"
    )

    out = None

    try:
        r = rq.delete(url, auth=(G["USER"], G["PASSWORD"]))

    except Exception as e:
        out = {"status" : -1, "http" : None, "data" :e}
    
    if not out:
        out = {"http" : r.status_code, "data" : None}
        if r.status_code == 200:
            out["status"] = 1
        
        else:
            out["status"] = 0
            out["data"] = e
    
    return out



def pgtbls_to_lyr(ws, dbname, tables, styles):
    """
    PostGIS Tables to Layers

    ws     = 'cos'
    dbname = 'gsrvcos'
    tables = [
        'cim_cos_18_l1', 'cim_cos_18_l2', 'cim_cos_18_l3', 'cim_cos_18_l4_v2',
        'cmb_cos_18_l1', 'cmb_cos_18_l2', 'cmb_cos_18_l3', 'cmb_cos_18_l4_v2',
        'cos_18_l1', 'cos_18_l2', 'cos_18_l3', 'cos_18_l4_v2',
    ]

    styles = {
        '/home/jasp/mrgis/gsrv/cos_18_l1.sld' : ['cim_cos_18_l1', 'cmb_cos_18_l1', 'cos_18_l1'],
        '/home/jasp/mrgis/gsrv/cos_18_l2.sld' : ['cim_cos_18_l2', 'cmb_cos_18_l2', 'cos_18_l2'],
        '/home/jasp/mrgis/gsrv/cos_18_l3.sld' : ['cim_cos_18_l3', 'cmb_cos_18_l3', 'cos_18_l3'],
        '/home/jasp/mrgis/gsrv/cos_18_l4.sld' : ['cim_cos_18_l4_v2', 'cmb_cos_18_l4_v2', 'cos_18_l4_v2'],
    }
    """

    from glass.pys.oss import fprop
    from glass.wg.gsrv.ws import create_ws
    from glass.wg.gsrv.st import add_pgstore
    from glass.wg.gsrv.sty import create_style, assign_style_to_layer

    # Create new Workspace
    create_ws(ws, overwrite=True)

    # Add new store
    store = ws + '_db'
    add_pgstore(store, ws, dbname)

    # Add new layers
    for t in tables:
        add_pglyr(t, ws, store, 3763)

    # Add styles
    for s in styles:
        sn = fprop(s, 'fn')
        create_style(sn, s)
        for l in styles[s]:
            assign_style_to_layer(sn, l)
    
    return True

