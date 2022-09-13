import os

OSM_API = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'osmdata',
    'osmapi'
)

OSM_BOUNDARY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'osmdata',
    'bound'
)

LULC_RESULT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'osmdata',
    'result'
)

OSM_SLD = {
    "URBAN_ATLAS"       : os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'osmdata',
        'sld', 'urban_atlas.sld'
    ),
    "CORINE_LAND_COVER" : os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'osmdata',
        'sld', 'corine_lc.sld'
    ),
    "GLOBE_LAND_30"     : os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'osmdata',
        'sld', 'globe_l30.sld'
    )
}

MAP_DOWNLOAD = LULC_RESULT