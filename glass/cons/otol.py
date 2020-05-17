"""
OSM2LULC constants
"""

import os

import json as js

from glass.sql.q import q_to_obj


OSM2LULC_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'osmtolulc.sqlite'
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


def nomenclature_id(nomenclature):
    """
    Return nomenclature ID
    """

    nom = q_to_obj(OSM2LULC_DB, (
        "SELECT fid, slug FROM nomenclatures "
        f"WHERE slug='{nomenclature}'"
    ), db_api='sqlite')

    if not nom.shape[0]:
        return 0
    
    return nom.iloc[0].fid


def classes_priority(nomid):
    """
    Return classes order by priority
    """

    classes = q_to_obj(OSM2LULC_DB, (
        "SELECT fid, bigbbox "
        "FROM lulc_classes "
        "WHERE priority IS NOT NULL AND "
        f"nomenclature = {str(nomid)} "
        "ORDER BY priority"
    ), db_api='sqlite')

    if not classes.shape[0]:
        return 0
    
    return classes.to_dict(orient="records")



def module_osmtags(nomid):
    """
    Return OSM Tags to be used in each OSM2LULC module
    """

    keycol  = DB_SCHEMA['OSM_FEATURES']['KEY']
    valcol  = DB_SCHEMA['OSM_FEATURES']['VALUE']
    lulcid  = DB_SCHEMA['OSM_LULC']['LULCID']
    bfcol   = DB_SCHEMA['OSM_LULC']['BUFFER']
    areacol = DB_SCHEMA['OSM_LULC']['AREA']
    module  = DB_SCHEMA['MODULES']['NAME']
    

    q = (
        f"SELECT ofeat.{keycol} AS {keycol}, "
        f"ofeat.{valcol} AS {valcol}, "
        f"jtbl.{module} AS {module}, jtbl.{lulcid} AS {lulcid}, "
        f"jtbl.{bfcol} AS {bfcol}, jtbl.{areacol} AS {areacol} "
        f"FROM {DB_SCHEMA['OSM_FEATURES']['TABLE']} AS ofeat "
        "INNER JOIN ("
            f"SELECT cosm.*, mod.{module} AS {module} "
            f"FROM {DB_SCHEMA['OSM_LULC']['TABLE']} AS cosm "
            f"INNER JOIN {DB_SCHEMA['MODULES']['TABLE']} AS mod "
            f"ON cosm.{DB_SCHEMA['OSM_LULC']['MODULE']} = "
            f"mod.{DB_SCHEMA['MODULES']['ID']} "
            f"INNER JOIN {DB_SCHEMA['LULC']['TABLE']} AS lcls "
            f"ON cosm.{lulcid} = lcls.{DB_SCHEMA['LULC']['ID']} "
            f"WHERE lcls.{DB_SCHEMA['LULC']['NOMENCLATURE']} = {nomid}"
        ") AS jtbl "
        f"ON ofeat.{DB_SCHEMA['OSM_FEATURES']['ID']} = "
        f"jtbl.{DB_SCHEMA['OSM_LULC']['OSMID']}"
    )

    return q_to_obj(OSM2LULC_DB, q, db_api='sqlite')


def get_legend(nomenclature, fid_col='fid', leg_col='leg'):
    """
    Return legend
    """

    tbl  = DB_SCHEMA["LULC"]["TABLE"]
    fid  = DB_SCHEMA["LULC"]["ID"]
    name = DB_SCHEMA["LULC"]["NAME"]
    nom  = DB_SCHEMA["LULC"]["NOMENCLATURE"]

    leg = q_to_obj(OSM2LULC_DB, (
        f"SELECT mtbl.{fid} AS {fid_col}, "
        f"mtbl.{name} AS {leg_col} "
        f"FROM {tbl} AS mtbl "
        f"WHERE mtbl.{nom}={nomenclature}"
    ), db_api='sqlite')

    return leg

