"""
OSM2LULC Utils
"""

from glass.cons.osmtolulc import OSM2LULC_DB, DB_SCHEMA, OSM_TABLES, GEOM_AREA
from glass.sql.q import q_to_obj


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


def osmfeat_by_rule(nomid):
    """
    Return OSM Features by rule and LULC class
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



def lulc_to_osmfeat(osmdb, nomenclature):
    """
    Add LULC Classes to OSM tags
    """

    from glass.sql.q import exec_write_q

    keycol = DB_SCHEMA["OSM_FEATURES"]["KEY"]
    valcol = DB_SCHEMA["OSM_FEATURES"]["VALUE"]
    lulcol = DB_SCHEMA['OSM_LULC']['LULCID']
    modcol = DB_SCHEMA['MODULES']['NAME']

    df = osmfeat_by_rule(nomenclature)

    df.loc[:, valcol] = df[keycol] + "='" + df[valcol] + "'"

    qs = []
    for mod in df[modcol].unique():
        fdf = df[df[modcol] == mod]

        otbl = 'lines' if mod == 'roads' or mod == 'basic_buffer' \
            else 'polygons'
        
        bfcol = DB_SCHEMA['OSM_LULC']['BUFFER'] if mod == 'roads' \
            or mod == 'basic_buffer' else None
        
        arcol = DB_SCHEMA['OSM_LULC']['AREA'] if mod == 'area_upper' \
            or mod == 'area_lower' else None
        
        fdf.loc[:, valcol] = OSM_TABLES[otbl] + "." + fdf[valcol]

        qs.append((
            f"ALTER TABLE {OSM_TABLES[otbl]} "
            f"ADD COLUMN {mod} integer"
        ))

        if bfcol:
            qs.append((
                f"ALTER TABLE {OSM_TABLES[otbl]} "
                f"ADD COLUMN bf_{mod} integer"
            ))
        
        if arcol:
            qs.append((
                f"ALTER TABLE {OSM_TABLES[otbl]} "
                f"ADD COLUMN t_{mod} integer"
            ))
        
        for c in fdf[lulcol].unique():
            _fdf = fdf[fdf[lulcol] == c]

            qs.append((
                f"UPDATE {OSM_TABLES[otbl]} SET {mod}={c} "
                f"WHERE {str(_fdf[valcol].str.cat(sep=' OR '))}"
            ))
        
        if bfcol:
            for bfdist in fdf[bfcol].unique():
                _fdf = fdf[fdf[bfcol] == bfdist]
                
                qs.append((
                    f"UPDATE {OSM_TABLES[otbl]} "
                    f"SET bf_{mod}={bfdist} "
                    f"WHERE {str(_fdf[valcol].str.cat(sep=' OR '))}"
                ))
        
        if arcol:
            for areaval in fdf[arcol].unique():
                _fdf = fdf[fdf[arcol] == areaval]
                
                qs.append((
                    f"UPDATE {OSM_TABLES[otbl]} "
                    f"SET t_{mod}={areaval} "
                    f"WHERE {str(_fdf[valcol].str.cat(sep=' OR '))}"
                ))
        
        if mod == 'buildings':
            refcls = 6 if nomenclature == 1 else 29
            fd = df[
                (df[modcol] == 'selection') & \
                (df[keycol] == 'building') & \
                (df[lulcol] == refcls)
            ]

            ptbl = OSM_TABLES['points']
            whr = str(fd[valcol].str.cat(sep=" OR "))

            qs += [
                f"ALTER TABLE {ptbl} ADD COLUMN {mod} integer",
                f"UPDATE {ptbl} SET {mod}={refcls} WHERE {whr}"
            ]
    
    exec_write_q(osmdb, qs, api='psql')


def osm_project(osm_db, epsg, isGlobeLand=None):
    """
    Reproject OSMDATA to a specific Spatial Reference System
    """
    
    from glass.sql.q        import q_to_ntbl
    from glass.prop.sql.idx import idx_for_geom
    from glass.ete.osm2lulc import GEOM_AREA

    geom_col = f"ST_Transform(wkb_geometry, {epsg})"
    
    osm_tbl = {}

    polycols = [
        "selection", "buildings", "area_upper",
        "area_lower", 
    ]

    polywhr = [f"{c} IS NOT NULL" for c in polycols]

    polycols += ["t_area_lower", "t_area_upper"]

    linescols = ["roads", "basic_buffer"]
    linesbf   = [f"bf_{c}" for c in linescols]
    lineswhr  = [f"{c} IS NOT NULL" for c in linescols]

    pntcol = "NULL AS buildings" if isGlobeLand else "buildings"
    pntwhr = "" if isGlobeLand else " WHERE buildings IS NOT NULL"

    osm_qs = {
        "polygons" : (
            f"SELECT building, {', '.join(polycols)}, "
            f"{geom_col} AS geometry, "
            f"ST_Area({geom_col}) AS {GEOM_AREA} "
            f"FROM {OSM_TABLES['polygons']} "
            f"WHERE {' OR '.join(polywhr)}"
        ) if not isGlobeLand else (
            f"SELECT building, selection, {geom_col} AS geometry "
            f"FROM {OSM_TABLES['polygons']} "
            "WHERE selection IS NOT NULL"
        ),
        "lines" : (
            "SELECT row_number() OVER(ORDER BY roads) AS gid, "
            f"{', '.join(linescols)}, {', '.join(linesbf)}, "
            f"lanes AS lanes, width, "
            f"{geom_col} AS geometry "
            f"FROM {OSM_TABLES['lines']} "
            f"WHERE {' OR '.join(lineswhr)}"
        ),
        "points" : (
            f"SELECT {pntcol}, {geom_col} AS geometry "
            f"FROM {OSM_TABLES['points']}{pntwhr}"
        )
    }
    
    for table in OSM_TABLES:
        nt = f'{table}_{str(epsg)}'
        
        q_to_ntbl(osm_db, nt, osm_qs[table], api='psql')
            
        idx_for_geom(osm_db, nt, "geometry")
        
        osm_tbl[table] = nt
    
    return osm_tbl

