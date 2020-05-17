"""
OpenStreetMap to Land Use/Land Cover Maps using PostGIS
"""

import os
import datetime as dt


def osm_to_lulc(osm, nomenclature, ref, outfld, outname, savedb=None, tmpfld=None):
    """
    Convert OSM Data into Land Use/Land Cover Information

    (Version 1.5)
    """

    # ************************************************************************ #
    # glass dependencies #
    # ************************************************************************ #
    from glass.ete.osm2lulc.mod1 import vec_selection
    from glass.ete.osm2lulc.mod2 import vec_roads
    from glass.ete.osm2lulc.m3_4 import vec_selbyarea
    from glass.ete.osm2lulc.mod5 import vect_bbuffer
    from glass.ete.osm2lulc.utilsv15 import nomenclature_id, get_mods_views
    
    from glass.prop.prj import get_epsg
    
    

    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    # Check if input parameters exists!
    if not os.path.exists(outfld):
        raise ValueError(f'{outfld} does not exist!')
    
    if not os.path.exists(osm):
        raise ValueError(f'File with OSM DATA ({osm}) does not exist!')
    
    if not os.path.exists(ref):
        raise ValueError(f'File with reference area ({ref}) does not exist!')
    
    # Check if Nomenclature is valid
    nom_id = nomenclature_id(nomenclature)

    if not nom_id:
        raise ValueError(f'Nomenclature {nomenclature} does not exist!')
    

    # Get EPSG
    epsg, isproj = get_epsg(ref, is_proj=True)

    epsg = 3857 if not isproj else epsg

    # Out GeoPackage
    gpkg = os.path.join(outfld, f"{outname}.gpkg")

    # ******************************************************************** #
    # Convert OSM file to PSQL DB #
    # ******************************************************************** #

    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    lyr_mod1, log_mod1 = vec_selection(
        osm_db, 'selection', gpkg, 'mod1_result'
    )
    time_d = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    lyr_mod2, log_mod2 = vec_roads(
        osm_db, 'roads', epsg,
        gpkg, 'mod2_result'
    )
    time_e = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    if nom_id != 3:
        lyr_mod3, log_mod3 = vec_selbyarea(
            osm_db, 'area_upper', gpkg, 'mod3_result',
            upper=True
        )
        
    else:
        log_mod3 = None
    
    time_f = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    if nom_id != 3:
        lyr_mod4, log_mod4 = vec_selbyarea(
            osm_db, 'area_lower', gpkg, 'mod4_result',
            upper=False
        )
    
    else:
        log_mod4 = None

    time_g = dt.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    lyr_mod5, log_mod5 = vect_bbuffer(
        osm_db, 'basic_buffer', gpkg, 'mod5_result'
    )
    time_h = dt.datetime.now().replace(microsecond=0)

    return gpkg, {
        0  : ('osm_to_sqdb', time_b - time_a),
        1  : ('modules_views', time_c - time_b),
        3  : ('module_1', time_d - time_c, log_mod1),
        4  : ('module_2', time_e - time_d, log_mod2),
        5  : None if not log_mod3 else ('module_3', time_f - time_e, log_mod3),
        6  : None if not log_mod4 else ('module_4', time_g - time_f, log_mod4),
        7  : ('module_5', time_h - time_g, log_mod5),
    }

