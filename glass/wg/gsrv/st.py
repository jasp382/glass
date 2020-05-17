"""
Tools to manage Stores in Geoserver
"""

import requests as rq
import os
from glass.firecons.gsrv import con_gsrv
from glass.pys.char import random_str
from glass.pys.oss import del_file
from glass.pys.Xml import write_xml_tree

def add_pgstore(dbname, ws, store):
    """
    Create new PSQL store
    """

    G  = con_gsrv()
    DB = G["DATABASE"]

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

    xml_tree = {
        "dataStore" : {
            "name"      : store,
            "type"      : "PostGIS",
            "enabled"   : "true",
            "workspace" : {
                "name"  : ws
            },
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
        }
    }

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

    # Send request to GeoServer
    with open(xml_file, 'rb') as f:
        try:
            r = rq.post(
                url, data=f, headers={'content-type' : 'text/xml'},
                auth=(G["USER"], G["PASSWORD"])
            )

            del_file(xml_file)

            return True, r
        
        except:
            del_file(xml_file)

            return None, None


def add_rststore(raster, ws, st):
    """
    Create a new store with a raster layer
    """

    G = con_gsrv()

    url = (
        f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
        f'geoserver/rest/workspaces/{ws}/'
        f'coveragestores?configure=all'
    )

    # Create obj with data to be written in the xml
    xmlTree = {
        "coverageStore" : {
            "name"      : st,
            "workspace" : ws,
            "enabled"   : "true",
            "type"      : "GeoTIFF",
            "url"       : raster
        }
    }

    treeOrder = {"coverageStore" : [
        "name", "workspace", "enabled", "type", "url"
    ]}

    # Write XML
    xml_file = write_xml_tree(xmlTree, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gsrvtmp', f'st_{random_str(7).lower()}.xml'
    ), nodes_order=treeOrder)

    # Send request
    with open(xml_file, 'rb') as f:
        try:
            r = rq.post(
                url, data=f, headers={'content-type' : 'text/xml'},
                auth=(G["USER"], G["PASSWORD"])
            )

            return True, r
        
        except:
            del_file(xml_file)

            return None, None

