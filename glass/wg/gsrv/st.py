"""
Tools to manage Stores in Geoserver
"""

import requests as rq
import os

from glass.cons.gsrv import con_gsrv
from glass.pys.char import random_str
from glass.pys.oss import del_file
from glass.pys.Xml import write_xml_tree


def lst_stores(work):
    """
    List all stores in a Workspace
    """
    
    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = f'{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/datastores'
    urlrst = f'{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/coveragestores'

    out = None
    
    try:
        r = rq.get(
            url, headers={'Accept': 'application/json'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    except Exception as e:
        out = {"status" : -1, "http" : None, "data" : f'cannot get datastores; {e}'}
    
    if not out:
        try:
            rr = rq.get(
                urlrst, headers={'Accept': 'application/json'},
                auth=(conf['USER'], conf['PASSWORD'])
            )
        
        except Exception as _e:
            out = {"status" : -1, "http" : None, "data" : f'cannot get coveragestores; {_e}'}
    
    if not out:
        try:
            _r = r.json()
            r_ = rr.json()

            d = [] if 'dataStore' not in _r["dataStores"] else \
                _r["dataStores"]['dataStore']
            
            c = [] if 'coverageStore' not in r_['coverageStores'] else \
                r_['coverageStores']['coverageStore']
            
            out = {
                "status" : 1,
                "data"   : {"dataStores" : d, "coverageStores" : c},
                "http"   : f"{r.status_code} -- {rr.status_code}"
            }
        
        except:
            out = {
                "status" : 0,
                "http"   : f"{r.status_code} -- {rr.status_code}",
                "data"  : str(r.content) + '\n' + str(rr.content)
            }
    
    return out


def lst_rststores(work):
    """
    List raster stores in a Workspace
    """
    
    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = f'{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/coveragestores'

    out = None
    
    try:
        r = rq.get(
            url, headers={'Accept': 'application/json'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    except:
        out = {"status" : -1}
    
    if not out:
        try:
            _r = r.json()

            d = [] if 'coverageStore' not in _r['coverageStores'] else \
                _r['coverageStores']['coverageStore']
            
            out = {
                "status" : 1,
                "json"   : d,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http"   : r.status_code,
                "content"  : str(r.content)
            }
    
    return out


def shp_to_store(shape, store_name, work, force_declared=None):
    """
    Create a new datastore
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']

    url = (
        f'{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/datastores/'
        f'{store_name}/file.shp'
    )
    
    out = None
    
    fn, ff = os.path.splitext(os.path.basename(shape))

    if ff != '.zip':
        from glass.pys.zzip import zip_files
        from glass.pys.oss import lst_ff, del_file

        shp_fld = os.path.dirname(shape)

        shape = os.path.join(shp_fld, f'{fn}.zip')

        del_file(shape)

        shapefiles = lst_ff(shp_fld, filename=fn)
        
        zip_files(shapefiles, shape)

    
    try:
        with open(shape, 'rb') as f:
            r = rq.put(
                url, data=f,
                headers={'content-type': 'application/zip'},
                auth=(conf['USER'], conf['PASSWORD'])
            )

            if force_declared:
                elm = {"featureType" : {
                    "srs" : f"EPSG:{str(force_declared)}",
                    "projectionPolicy" : "REPROJECT_TO_DECLARED"
                }}

                xmlfile = write_xml_tree(elm, os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'tmpxml', f'upst_{random_str(7).lower()}.xml'
                ))

                with open(xmlfile, 'rb') as __xml:
                    nr = rq.put((
                        f"{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/"
                        f"datastores/{store_name}/featuretypes/{fn}"
                    ), data=__xml, headers={'content-type' : 'text/xml'},
                    auth=(conf['USER'], conf['PASSWORD']))

        
    except Exception as e_:
        out = {"status" : -1, "http" : None, "data" : str(e_)}

    if not out:
        if r.status_code == 201:
            out = {
                "status" : 1,
                "data"   : {"store" : store_name},
                "http"   : r.status_code
            }
        
        else:
            out = {
                "status" : 0,
                "http"   : r.status_code,
                "data"   : str(r.content)
            }
    
    return out


def add_rststore(raster, ws, st):
    """
    Create a new store with a raster layer
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = (
        f'{_p}://{h}:{p}/geoserver/rest/workspaces/{ws}/'
        'coveragestores?configure=all'
    )
    
    out = None

    # Create obj with data to be written in the xml
    xmlTree = {"coverageStore" : {
        "name"      : st,
        "workspace" : ws,
        "enabled"   : "true",
        "type"      : "GeoTIFF",
        "url"       : raster
    }}

    treeOrder = {"coverageStore" : [
        "name", "workspace", "enabled", "type", "url"
    ]}

    # Write XML
    xml_file = write_xml_tree(xmlTree, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gsrvtmp', f'st_{random_str(7).lower()}.xml'
    ), nodes_order=treeOrder)

    # Send request
    try: 
        with open(xml_file, 'rb') as f:
            r = rq.post(
                url, data=f, headers={'content-type' : 'text/xml'},
                auth=(conf["USER"], conf["PASSWORD"])
            )

            del_file(xml_file)
        
    except Exception as _e:
        out = {"status" : -1, "http" : None, "data" : str(_e)}
    
    if not out:
        if r.status_code == 201:
            out = {
                "status" : 1,
                "data" : {"store" : st},
                "http" : r.status_code
            }

        else:
            out = {
                "status" : 0,
                "http"   : r.status_code,
                "data"   : str(r.content)
            }
    
    return out


def add_pgstore(dbname, ws, store):
    """
    Create new PSQL store
    """

    from glass.cons.psql import con_psql

    G, DB  = con_gsrv(), con_psql()

    # Create obj with data to be written in the xml
    tree_order = {
        "dataStore": [
            "name", "type", "enabled", "workspace",
            "connectionParameters", "__default"
        ],
        "connection:Parameters": [
            ("entry", "key", "port"), ("entry", "key", "user"),
            ("entry", "key", "passwd"), ("entry", "key", "dbtype"),
            ("entry", "key", "host"), ("entry", "key", "database"),
            ("entry", "key", "schema")
        ]
    }

    xml_tree = {"dataStore" : {
        "name"      : store,
        "type"      : "PostGIS",
        "enabled"   : "true",
        "workspace" : {"name": ws},
        "connectionParameters" : {
            ("entry", "key", "port")     : DB["PORT"],
            ("entry", "key", "user")     : DB["USER"],
            ("entry", "key", "passwd")   : DB["PASSWORD"],
            ("entry", "key", "dbtype")   : "postgis",
            ("entry", "key", "host")     : DB["HOST"],
            ("entry", "key", "database") : dbname,
            ("entry", "key", "schema")   : "public"
        },
        "__default" : "false"
    }}

    # Write XML
    xml_file = write_xml_tree(xml_tree, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gsrvtmp', f'st_{random_str(7).lower()}.xml'
    ), nodes_order=tree_order)

    # Create GeoServer Store
    url = (
        f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
        f'geoserver/rest/workspaces/{ws}/datastores.xml'
    )
        
    out = None

    # Send request to GeoServer
    try:
        with open(xml_file, 'rb') as f:
            r = rq.post(
                url, data=f, headers={'content-type' : 'text/xml'},
                auth=(G["USER"], G["PASSWORD"])
            )

            del_file(xml_file)
        
    except Exception as _e:
        del_file(xml_file)

        out = {"status" : -1, "http" : None, "data" : str(_e)}
        
    if not out:
        txt = r.content.decode('utf-8')

        if r.status_code == 201:
            out = {
                "status" : 1,
                "data"   : {"store" : store},
                "http"   : r.status_code
            }
        
        elif r.status_code == 403:
            wsref = f'Expected workspace {ws} but client specified null'

            out = {
                "status" : 0,
                "http"   : r.status_code,
                "data"   : "Workspace doesn't exist" if wsref in txt else txt
            }

        elif r.status_code == 500:
            stref = f"Store '{store}' already exists in workspace '{ws}'"

            out = {
                "status" : 0,
                "http"   : r.status_code,
                "data"   : "Store already exists" if stref == txt else txt
            }
        
        else:
            out = {
                "status" : 0,
                "http"   : r.status_code,
                "data"   : txt
            }
    
    return out


def del_store(work, name, isrst=None):
    """
    Delete an existing Geoserver datastore
    """
    
    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = (
        f'{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/'
        f'datastores/{name}?recurse=true'
    ) if not isrst else (
        f'{_p}://{h}:{p}/geoserver/rest/workspaces/{work}/'
        f'coveragestores/{name}?recurse=true'
    )

    out = None

    try:
        r = rq.delete(url, auth=(conf['USER'], conf['PASSWORD']))
    
    except Exception as e:
        out = {"status" : -1, "http" : None, "data" : str(e)}
    
    if not out:
        if r.status_code == 200:
            out = {
                "status" : 1,
                "data"   : None,
                "http"   : r.status_code
            }
        
        else:
            out = {
                "status" : 0,
                "data"   : r.status_code,
                "content" : str(r.content)
            }
    
    return out


def import_datafolder(path_folder, store_name, workspace):
    """
    Import all shapefiles in a directory to a GeoServer Store
    """
    
    conf = con_gsrv()

    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/datastores/'
        '{store}/external.shp?configure=all'
        ).format(
            host=conf['HOST'], port=conf['PORT'], work=workspace,
            store=store_name, pro=conf['PROTOCOL']
        )

    r = rq.put(
        url,
        data=f'file://{path_folder}',
        headers={'content-type': 'text/plain'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    return r

