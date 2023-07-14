"""
OpenStreetMap to Land Use/Land Cover Maps using PostGIS
"""

import os
import datetime as dt


def osm_to_lulc(osm, nomenclature, epsg, outfile, savedb=None, tmpfld=None):
    """
    Convert OSM Data into Land Use/Land Cover Information

    (Version 1.5)
    """

    # ************************************************************************ #
    # glass dependencies #
    # ************************************************************************ #
    from glass.cons.otol import OTOL_LULC
    from glass.dtt.mge import shps_to_shp
    from glass.ete.otol.tools import nomenclature_id, module_osmtags
    from glass.ete.otol.tools import get_legend
    from glass.ete.otol.vec import module_1, module_2, module_3_and_4, module_5
    from glass.ete.otol.vec import module_6
    from glass.it.db             import osm_to_psql
    from glass.pys.oss import fprop
    from glass.pys.tm import now_as_str
    from glass.rd.shp import shp_to_obj
    from glass.sql.db           import create_db, drop_db
    from glass.wt.shp import df_to_shp

    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    if not os.path.exists(osm):
        raise ValueError(f'File with OSM DATA ({osm}) does not exist!')
    
    if not os.path.exists(os.path.dirname(outfile)):
        raise ValueError(f'{os.path.dirname(outfile)} does not exist!')
    
    # Check if outfile is a geopackage or not
    
    # Check if Nomenclature is valid
    nom_id = nomenclature_id(nomenclature)

    if not nom_id:
        raise ValueError(f'Nomenclature {nomenclature} does not exist!')
    
    # Get classes names
    leg_df = get_legend(nom_id, fid_col='fid')
    
    # Todo: check if EPSG is Projected or not

    # Workspace
    ws = tmpfld if tmpfld else os.path.join(
        os.path.dirname(osm),
        now_as_str(utc=True)
    )

    # Create intermediate geopackage
    tmpgpkg = os.path.join(ws, 'modules_res.gpkg')
    tmplyrs = []

    # ******************************************************************** #
    # Get OSM Tags that should be used in each OSM2LULC module #
    # ******************************************************************** #
    time_a = dt.datetime.now().replace(microsecond=0)
    mod_tags = module_osmtags(nom_id)

    time_b = dt.datetime.now().replace(microsecond=0)

    # ******************************************************************** #
    # Convert OSM file to PSQL DB #
    # ******************************************************************** #
    osm_db = create_db(fprop(osm, 'fn', forceLower=True), overwrite=True)
    osm_db = osm_to_psql(osm, osm_db)

    time_c = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # MODULE 1 - Select and dissolve #
    # ************************************************************************ #
    mod1, log1 = module_1(mod_tags, osm_db, epsg, tmpgpkg, 'module_1')
    tmplyrs.append(mod1)

    time_d = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # MODULE 2 - Get Information About Roads Location #
    # ************************************************************************ #
    mod2, log2 = module_2(mod_tags, osm_db, epsg, tmpgpkg, 'module_2')
    tmplyrs.append(mod2)

    time_e = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # MODULE 3 - Area Upper than #
    # ************************************************************************ #
    if nom_id != 3:
        mod3, log3 = module_3_and_4(
            mod_tags, osm_db, epsg, tmpgpkg, 'module_3',
            upper=True
        )

        tmplyrs.append(mod3)
    
    else:
        mod3, log3 = None, None
    
    time_f = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # MODULE 4 - Area Lower than #
    # ************************************************************************ #
    if nom_id != 3:
        mod4, log4 = module_3_and_4(
            mod_tags, osm_db, epsg, tmpgpkg, 'module_4',
            upper=False
        )
        tmplyrs.append(mod4)
    
    else:
        mod4, log4 = None, None
    
    time_g = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # MODULE 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    mod5, log5 = module_5(mod_tags, osm_db, epsg, tmpgpkg, 'module_5')

    tmplyrs.append(mod5)

    time_h = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # MODULE 6 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nom_id != 3:
        mod6, log6 = module_6(mod_tags, osm_db, epsg, tmpgpkg, 'module_6')

        tmplyrs.append(mod6)
    else:
        mod6, log6 = None, None

    time_i = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # Merge Modules results in one layer #
    # ************************************************************************ #
    shps_to_shp(
        tmpgpkg, outfile, api="gpkg_to_gpkg",
        olyrname='osmtolulc_v1', gpkglyrs=tmplyrs
    )

    # Add classes names to the result produced before
    lulc_df = shp_to_obj(outfile, lyr='osmtolulc_v1')

    lulc_df = lulc_df.merge(
        leg_df, how='left',
        left_on=OTOL_LULC, right_on='fid'
    )

    lulc_df.drop('fid', axis=1, inplace=True)

    df_to_shp(lulc_df, outfile, layername='osmtolulc_v2')

    return outfile, {
        0  : ('get_modules_tags_classes', time_b - time_a),
        1  : ('osm_to_db', time_c - time_b),
        2  : ('module_1', time_d - time_c, log1),
        3  : ('module_2', time_e - time_d, log2),
        4  : None if not log3 else ('module_3', time_f - time_e, log3),
        5  : None if not log4 else ('module_4', time_g - time_f, log4),
        6  : ('module_5', time_h - time_g, log5),
        7  : None if not log6 else ('module_6', time_i - time_h, log5),
    }

