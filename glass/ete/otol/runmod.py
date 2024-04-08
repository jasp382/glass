"""
Run OSM2LULC Modules individualy
"""

import os

def run_mod2(osm, epsg, ofile, olyr=None):
    """
    Run Module to Extract Roads
    """

    nomenclature = 'uatlas'

    # ************************************************************************ #
    # glass dependencies #
    # ************************************************************************ #
    from glass.cons.otol    import OTOL_LULC, nomenclature_id, module_osmtags
    from glass.ete.otol.vec import module_2
    from glass.it.db        import osm_to_psql
    from glass.pys.oss      import fprop
    from glass.sql.db       import create_pgdb
    from glass.it.shp       import shp_to_shp

    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    if not os.path.exists(osm):
        raise ValueError(f'File with OSM DATA ({osm}) does not exist!')
    
    # Check if outfile is a geopackage or not
    if os.path.splitext(ofile)[-1] != '.gpkg':
        tmpgpkg = os.path.join(os.path.dirname(ofile), f'{fprop(ofile, "fn")}.gpkg')

        needexp = True
    
    else:
        tmpgpkg = ofile
        needexp = None
    
    # Check if Nomenclature is valid
    nom_id = nomenclature_id(nomenclature)

    if not nom_id:
        raise ValueError(f'Nomenclature {nomenclature} does not exist!')
    
    # ******************************************************************** #
    # Get OSM Tags that should be used in each OSM2LULC module #
    # ******************************************************************** #
    mod_tags = module_osmtags(nom_id)

    # ******************************************************************** #
    # Convert OSM file to PSQL DB #
    # ******************************************************************** #
    osm_db = create_pgdb(fprop(osm, 'fn', forceLower=True), overwrite=True)
    osm_db = osm_to_psql(osm, osm_db)

    # ************************************************************************ #
    # MODULE 2 - Get Information About Roads Location #
    # ************************************************************************ #
    mod2, log2 = module_2(
        mod_tags, osm_db, epsg, tmpgpkg,
        'module_2' if not olyr else olyr
    )

    if not needexp:
        return tmpgpkg
    
    shp_to_shp(tmpgpkg, ofile, lyrname=mod2)

    return ofile

