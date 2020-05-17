"""
Tools for Geoserver datastores management
"""


def shp_to_store(shape, store_name, workspace):
    """
    Create a new datastore
    """

    import os;           import requests
    from glass.pyt.oss   import lst_ff, fprop
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()

    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/datastores/'
        '{store}/file.shp'
        ).format(
            host=conf['HOST'], port=conf['PORT'], work=workspace,
            store=store_name, pro=conf['PROTOCOL']
        )
    
    shpp = fprop(shape, ['fn', 'ff'])
    fn, ff = shpp['filename'], shpp['fileformat']

    if ff != '.zip':
        from glass.pyt.ff.zzip import zip_files

        shp_fld = os.path.dirname(shape)

        shapefiles = lst_ff(shp_fld, filename=fn)

        shape = os.path.join(shp_fld, fn + '.zip')
        zip_files(shapefiles, shape)

    with open(shape, 'rb') as f:
        r = requests.put(
            url,
            data=f,
            headers={'content-type': 'application/zip'},
            auth=(conf['USER'], conf['PASSWORD'])
        )

        return r


def import_datafolder(path_folder, store_name, workspace):
    """
    Import all shapefiles in a directory to a GeoServer Store
    """

    import requests
    from glass.cons.gsrv import con_gsrv
    
    conf = con_gsrv()

    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/datastores/'
        '{store}/external.shp?configure=all'
        ).format(
            host=conf['HOST'], port=conf['PORT'], work=workspace,
            store=store_name, pro=conf['PROTOCOL']
        )

    r = requests.put(
        url,
        data='file://' + path_folder,
        headers={'content-type': 'text/plain'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    return r


def lst_stores(workspace):
    """
    List all stores in a Workspace
    """
    
    import requests;    import json
    from glass.cons.gsrv import con_gsrv
    
    conf = con_gsrv()
    
    url = '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/datastores'.format(
        host=conf['HOST'], port=conf['PORT'], work=workspace, pro=conf['PROTOCOL']
    )
    
    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )
    
    ds = r.json()
    if 'dataStore' in ds['dataStores']:
        return [__ds['name'] for __ds in ds['dataStores']['dataStore']]
    else:
        return []


def del_store(workspace, name):
    """
    Delete an existing Geoserver datastore
    """
    
    import requests
    import json
    from glass.cons.gsrv import con_gsrv
    
    conf = con_gsrv()
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/'
        'datastores/{ds}?recurse=true'
    ).format(
        host=conf['HOST'], port=conf['PORT'], work=workspace, ds=name,
        pro=conf['PROTOCOL']
    )
    
    r = requests.delete(url, auth=(conf['USER'], conf['PASSWORD']))
    
    return r


def add_rst_store(raster, store_name, workspace):
    """
    Create a new store with a raster layer
    """
    
    import os;        import requests
    from glass.pyt.oss import del_file
    from glass.pyt.Xml import write_xml_tree
    from glass.cons.gsrv import con_gsrv
    
    conf = con_gsrv()
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}/'
        'coveragestores?configure=all'
    ).format(
        host=conf['HOST'], port=conf['PORT'],
        work=workspace, pro=conf['PROTOCOL']
    )
    
    # Create obj with data to be written in the xml
    xmlTree = {
        "coverageStore" : {
            "name"   : store_name,
            "workspace": workspace,
            "enabled": "true",
            "type"   : "GeoTIFF",
            "url"    : raster
        }
    }
    
    treeOrder = {
        "coverageStore" : ["name", "workspace", "enabled", "type", "url"]
    }
    
    # Write XML
    xml_file = write_xml_tree(
        xmlTree,
        os.path.join(os.path.dirname(raster), 'new_store.xml'),
        nodes_order=treeOrder
    )
    
    # Send request
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url,
            data=f,
            headers={'content-type': 'text/xml'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    del_file(xml_file)
        
    return r


"""
PostGIS stores creation
"""


def create_pgstore(store, workspace, db, dbset='default'):
    """
    Create a store for PostGIS data
    """
    
    import os;           import requests
    from glass.pyt.char  import random_str
    from glass.pyt.Xml   import write_xml_tree
    from glass.pyt.oss   import mkdir, del_folder
    from glass.cons.gsrv import con_gsrv
    from glass.cons.psql import con_psql
    
    gs_con = con_gsrv()
    pg_con = con_psql(db_set=dbset)
    
    # Create folder to write xml
    wTmp = mkdir(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            random_str(7)
        )
    )
    
    # Create obj with data to be written in the xml
    tree_order = {
        "dataStore": ["name", "type", "enabled", "workspace",
                      "connectionParameters", "__default"],
        "connection:Parameters": [
            ("entry", "key", "port"), ("entry", "key", "user"),
            ("entry", "key", "passwd"), ("entry", "key", "dbtype"),
            ("entry", "key", "host"), ("entry", "key", "database"),
            ("entry", "key", "schema")
        ]
    }
    
    xml_tree = {
        "dataStore" : {
            "name"      : store,
            "type"      : "PostGIS",
            "enabled"   : "true",
            "workspace" : {
                "name"  : workspace
            },
            "connectionParameters" : {
                ("entry", "key", "port")     : pg_con["PORT"],
                ("entry", "key", "user")     : pg_con["USER"],
                ("entry", "key", "passwd")   : pg_con["PASSWORD"],
                ("entry", "key", "dbtype")   : "postgis",
                ("entry", "key", "host")     : pg_con["HOST"],
                ("entry", "key", "database") : db,
                ("entry", "key", "schema")   : "public"
            },
            "__default" : "false"
        }
    }
    
    # Write xml
    xml_file = write_xml_tree(
        xml_tree, os.path.join(wTmp, 'pgrest.xml'), nodes_order=tree_order
    )
    
    # Create Geoserver Store
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{wname}/'
        'datastores.xml'
    ).format(
        host=gs_con['HOST'], port=gs_con['PORT'],
        wname=workspace, pro=gs_con['PROTOCOL']
    )
    
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url,
            data=f,
            headers={'content-type': 'text/xml'},
            auth=(gs_con['USER'], gs_con['PASSWORD'])
        )
        f.close()
    
    del_folder(wTmp)
    
    return r

