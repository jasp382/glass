""" Global Variables """

import os


DB_SCHEMA = {
    "RULES" : {
        "NAME"         : "rules",
        "RULE_ID"      : "fid",
        "RULE_NAME"    : "name"
    },
    "OSM_FEATURES" : {
        "NAME"      : "osm_features",
        "OSM_ID"    : "id",
        "OSM_KEY"   : "key",
        "OSM_VALUE" : "value"
    },
    "CORINE_LAND_COVER"  : {
        "NAME"         : "nom_corine_lc",
        "CLS_ID"       : "clc_id",
        "OSM_RELATION" : "osm_clc",
        "OSM_FK"       : "osm_id",
        "CLS_FK"       : "clc_id",
        "RULE_FK"      : "rule_id",
        "RULES_FIELDS" : {"BUFFER" : "buffer_dist", "AREA" : "area"}
    },
    "URBAN_ATLAS" : {
        "NAME"         : "nom_urban_atlas",
        "CLS_ID"       : "ua_id",
        "OSM_RELATION" : "osm_ua",
        "OSM_FK"       : "osm_id",
        "CLS_FK"       : "ua_id",
        "RULE_FK"      : "rule_id",
        "RULES_FIELDS" : {"BUFFER" : "buffer_dist", "AREA" : "area"}
    },
    "GLOBE_LAND_30"    : {
        "NAME"         : "nom_globe_lc",
        "CLS_ID"       : "globe_id",
        "OSM_RELATION" : "osm_globe",
        "OSM_FK"       : "osm_id",
        "CLS_FK"       : "globe_id",
        "RULE_FK"      : "rule_id",
        "RULES_FIELDS" : {"BUFFER" : "buffer_dist", "AREA" : "area"}
    }
}

PROCEDURE_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'osmtolulc.sqlite'
)

osmTableData = {
    'polygons' : 'multipolygons',
    'lines'    : 'lines',
    'points'   : 'points'
}

PRIORITIES = {
    "URBAN_ATLAS"       : [
        1222, 1221, 12, 5, 14, 13, 11, 2, 3
    ],
    "CORINE_LAND_COVER" : [
        1222, 1221, 12, 52, 51, 4, 142, 1421, 141, 13, 11, 22,
        23, 21, 24, 2, 324, 321, 33, 31
    ],
    "GLOBE_LAND_30"     : [
        802, 801, 80, 60, 50, 10, 30, 20, 40, 90, 100
    ],
    "URBAN_ATLAS_NUMPY" : [
        98, 99, 12, 5, 14, 13, 11, 2, 3
    ],
    "CORINE_LAND_COVER_NUMPY" : [
        98, 99, 12, 52, 51, 4, 97, 96, 95, 13, 11,
        22, 23, 21, 24, 2, 93, 94, 33, 31
    ],
    "GLOBE_LAND_30_NUMPY" : [
        82, 81, 80, 60, 50, 10, 30, 20, 40, 90, 100
    ]
}

GEOM_AREA = "geom_area"

LEGEND = {
    "URBAN_ATLAS" : {
        1222 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        1221 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        14 : "Artificial non-agricutural vegetated areas",
        2 : "Agricultural, semi-natural areas, wetlands",
        3 : "Forests",
        5 : "Water"
    },
    "CORINE_LAND_COVER" : {
        1222 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        1221 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        141 : "Green urban areas (Level 3)",
        142 : "Sport and leisure facilities (Level 3)",
        1421 : "Sport and leisure facilities (Level 3)",
        2  : "Agricultural areas (Level 1)",
        21 : "Arable Land (Level 2)",
        22 : "Permanent crops (Level 2)",
        23 : "Pastures (Level 2)",
        24 : "Heterogeneous agricultural areas (Level 2)",
        31 : "Forests",
        321 : "Natural grasslands",
        324 : "Transitional woodland-shrub",
        33 : "Open spaces with little or no vegetation",
        51 : "Inland waters",
        52 : "Marine waters",
        4  : "Wetlands"
    },
    "GLOBE_LAND_30" : {
        801 : "Artificial surfaces",
        802 : "Artificial surfaces",
        80  : "Artificial surfaces",
        60  : "Water bodies",
        50  : "Wetland",
        10  : "Cultivated land",
        30  : "Grassland",
        20  : "Forests",
        40  : "Scrubland",
        90  : "Bareland",
        70  : "Tundra",
        100 : "Permanent snow/ice"
    },
    "URBAN_ATLAS_NUMPY" : {
        98 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        99 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        14 : "Artificial non-agricutural vegetated areas",
        2 : "Agricultural, semi-natural areas, wetlands",
        3 : "Forests",
        5 : "Water"
    },
    "CORINE_LAND_COVER_NUMPY" : {
        98 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        99 : ("Industrial, commercial, public, military, "
                "private and transport units"),
        11 : "Urban Fabric",
        12 : ("Industrial, commercial, public, military, "
              "private and transport units"),
        13 : "Mine, dump and construction sites",
        2  : "Agricultural areas",
        21 : "Arable Land",
        22 : "Permanent crops",
        23 : "Pastures",
        24 : "Heterogeneous",
        31 : "Forests",
        33 : "Open spaces with little or no vegetation",
        51 : "Inland waters",
        52 : "Marine waters",
        4  : "Wetlands",
        95 : "Green urban areas (Level 3)",
        97 : "Sport and leisure facilities (Level 3)",
        96 : "Sport and leisure facilities (Level 3)",
        94 : "Natural grasslands",
        93 : "Transitional woodland-shrub",
    },
    "GLOBE_LAND_30_NUMPY" : {
        82  : "Artificial surfaces",
        81  : "Artificial surfaces",
        80  : "Artificial surfaces",
        60  : "Water bodies",
        50  : "Wetland",
        10  : "Cultivated land",
        30  : "Grassland",
        20  : "Forests",
        40  : "Scrubland",
        90  : "Bareland",
        70  : "Tundra",
        100 : "Permanent snow/ice"
    }
}


"""
Execute OSM2LULC Algorithm
"""
def osm_to_lulc(__VERSION, OSM_DATA, NOMENCLATURE, REF_RASTER, RESULT,
                SRS_CODE=3857, REWRITE=None, DATAFOLDER=None):
    """
    __VERSION options:
    * GRASS_VECTOR;
    * GRASS_SQLITE_VECTOR;
    * GRASS_RASTER;
    * NUMPY_RASTER.
    
    ROADS OPTIONS:
    * GRASS;
    * SQLITE.
    """
    
    if __VERSION == "GRASS_RASTER":
        from glass.sds.osm2lulc.grs import raster_based
        
        rr = raster_based(
            OSM_DATA, NOMENCLATURE, REF_RASTER, RESULT,
            overwrite=REWRITE, dataStore=DATAFOLDER
        )
    
    elif __VERSION == "GRASS_VECTOR":
        from glass.sds.osm2lulc.grs import vector_based
        
        rr = vector_based(
            OSM_DATA, NOMENCLATURE, REF_RASTER, RESULT,
            overwrite=REWRITE, dataStore=DATAFOLDER,
            RoadsAPI="GRASS"
        )
    
    elif __VERSION == "GRASS_SQLITE_VECTOR":
        from glass.sds.osm2lulc.grs import vector_based
        
        rr = vector_based(
            OSM_DATA, NOMENCLATURE, REF_RASTER, RESULT,
            overwrite=REWRITE, dataStore=DATAFOLDER,
            RoadsAPI="SQLITE"
        )
    
    elif __VERSION == "NUMPY_RASTER":
        from glass.sds.osm2lulc.num import osm2lulc
        
        rr = osm2lulc(
            OSM_DATA, NOMENCLATURE, REF_RASTER, RESULT,
            overwrite=REWRITE, dataStore=DATAFOLDER
        )
    
    else:
        raise ValueError('Version with tag {} is not available')
    
    return rr

