"""
OSM2LULC constants
"""

import os

import json as js


OSM2LULC_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'ete', 'otol', 'osm2lulc_v15.sqlite'
)

DB_SCHEMA = {
    "MODULES" : {
        "TABLE" : "modules",
        "ID"    : "fid",
        "NAME"  : "name"
    },
    "OSM_FEATURES" : {
        "TABLE" : "osm_features",
        "ID"    : "id",
        "KEY"   : "key",
        "VALUE" : "value"
    },
    "LULC" : {
        "TABLE" : "lulc_classes",
        "ID" : "fid",
        "CODE" : "code",
        "NAME" : "name",
        "NOMENCLATURE" : "nomenclature"
    },
    "OSM_LULC" : {
        "TABLE"  : "class_osm",
        "OSMID"  : "osm_id",
        "LULCID" : "lulc_id",
        "MODULE" : "module",
        "BUFFER" : "buffer_dist",
        "AREA"   : "area"
    }
}

OSM_TABLES = {
    'polygons' : 'multipolygons',
    'lines'    : 'lines',
    'points'   : 'points'
}

GEOM_AREA = 'geom_area'

OSM_PK   = 'ogc_fid'
OSM_GEOM = 'wkb_geometry'

OTOL_MODULE = "osm_module"
OTOL_GEOM = 'geometry'
OTOL_LULC = 'lulc'

CLASS_PRIORITY = {
    'uatlas' : [22, 21, 6, 4, 8, 7, 5, 2, 3],
    'clc' : [
        87, 86, 29, 42, 41, 26, 103, 89, 102,
        30, 28, 33, 34, 32, 35, 24, 70, 67, 38, 36
    ],
    'glob' : [101, 100, 90, 91, 92, 94, 95, 93, 96, 97, 98]
}


def osm_features():
    """
    Return OSM Features and their relation
    with LULC classes and OSM2LULC Modules
    """

    import pandas as pd

    jf = js.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'osmtags_to_lulc.json'
    ), 'r'))

    return pd.DataFrame(jf)

