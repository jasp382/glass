"""
OSM2LULC Support Tools
"""

from glass.cons.otol import OSM2LULC_DB, DB_SCHEMA
from glass.sql.q     import q_to_obj


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
    
    else:
        return nom.iloc[0].fid



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

