"""
Extract OSM data using queries
"""


def get_osm_with_refclasses(osm_ref_tags, osmdata, ref_classes, oshp,
    epsg=4326, clscol="lulc_cls"):
    """
    Get OSM data with tags related to classes in 
    ref_classes

    osm_ref_tags = {
        "TABLE"     : '/home/jasp/mystuff/dgt/osm_features_2021_v2.xlsx',
        "SHEET"     : 'osm_features',
        "LULC_COL"  : 'L4',
        "KEY_COL"   : "key",
        "VALUE_COL" : "value",
        "GEOM_COL"  : "geom"
    }

    osmdata = {
        "FILE"  : '/home/jasp/mystuff/dgt/tstcoimbra/osm_cmb.xml',
        "DB"    : 'dgt_cmb',
        "TABLE" : "multipolygons",
        "DBSET" : "local"
    }

    ref_classes = [
        '1141', '1151', '1211', '1221',
        '1222', '1223', '1231', '1241',
        '1251', '1252', '1254', '1255',
        '1256', '1257', '1253', '1612',
        '1631', '1632', '1633', '1651',
        '16', '143', '1431', '1432'
    ]

    clscol = 'lulc_cls'
    """

    from glass.sql.db   import create_db
    from glass.it.db    import osm_to_psql
    from glass.rd       import tbl_to_obj
    from glass.prop.sql import cols_name
    from glass.sql.q    import exec_write_q
    from glass.it.shp   import dbtbl_to_shp

    epsg = 4326 if not epsg else epsg
    clscol = 'lulc_cls' if not clscol or type(clscol) != str else clscol

    # Import data into a database
    create_db(osmdata["DB"], api='psql', overwrite=True, dbset=osmdata["DBSET"])

    osm_to_psql(osmdata["FILE"], osmdata["DB"], dbsetup=osmdata["DBSET"])

    # Get osmtags in reference table
    osm_tags = tbl_to_obj(osm_ref_tags["TABLE"], sheet=osm_ref_tags["SHEET"])

    osm_tags = osm_tags[osm_tags[osm_ref_tags["GEOM_COL"]] == 'Polygon']

    osm_tags[osm_ref_tags["LULC_COL"]] = osm_tags[osm_ref_tags["LULC_COL"]].astype(str)
    osm_tags['sevtags'] = osm_tags[osm_ref_tags["LULC_COL"]].str.contains(';')

    osm_tags = osm_tags[osm_tags.sevtags != True]

    # Create key/value column
    osm_tags.loc[:, osm_ref_tags["VALUE_COL"]] = osmdata["TABLE"] + "." + \
        osm_tags[osm_ref_tags["KEY_COL"]] + \
            "='" + osm_tags[osm_ref_tags["VALUE_COL"]] + "'"
    
    # Add new column to multipolygons table
    # Update it adding an LULC class

    cols = cols_name(osmdata["DB"], osmdata['TABLE'], dbset=osmdata["DBSET"])

    qs = [] if clscol in cols else [(
        f"ALTER TABLE {osmdata['TABLE']} ADD COLUMN "
        f"{clscol} integer"
    )]

    for cls in osm_tags[osm_ref_tags["LULC_COL"]].unique():
        # Se uma feature estiver associada a duas TAGS que dizem respeito a classes
        # diferentes, a classe da feature será a última classe considerada
        # Abordagem multitag vai resolver este problema.
        __osmtags = osm_tags[osm_tags[osm_ref_tags["LULC_COL"]] == cls]
    
        qs.append((
            f"UPDATE {osmdata['TABLE']} SET {clscol}={str(cls)} "
            f"WHERE {str(__osmtags[osm_ref_tags['VALUE_COL']].str.cat(sep=' OR '))}"
        ))
    
    # RUN queries
    exec_write_q(osmdata["DB"], qs, api='psql', dbset=osmdata["DBSET"])

    # Export shapefile with data
    whr = " OR ".join([f"{clscol}={c}" for c in ref_classes])

    q = (
        f'SELECT ogc_fid, osm_id, name, {clscol}, '
        'building, amenity, landuse, '
        f'ST_Transform(wkb_geometry, {str(epsg)}) AS geom '
        f'FROM {osmdata["TABLE"]} '
        f'WHERE {whr}'
    )

    try:
        dbtbl_to_shp(
            osmdata["DB"], q, 'geom', oshp,
            tableIsQuery=True, api='pgsql2shp', epsg=epsg,
            dbset=osmdata["DBSET"]
        )
    except:
        print('No data to export from PostgreSQL')

        return None

    return oshp


def osm_to_lucls_mtag(reftbl, osm, lucls, oshp, epsg=4326, lucol=None):
    """
    Return OSM data related to classes in ref_classes

    reftbl = {
        "TABLE"     : '/mnt/disk1/jasp/dgtinescc/multitags_to_classes.xlsx',
        "SHEET"     : 'final_table',
        "LULC_COL"  : 'l4'
    }

    osm = {
        "FILE"  : '/mnt/disk1/jasp/dgtinescc/osm_parts/osmpt_177.xml',
        "DB"    : 'dbosm_177',
        "TABLE" : "multipolygons",
        "DBSET" : "local"
    }

    lucls = [
        '11', '12', '13', '14', '16',
        '114', '121', '122', '125', '131',
        '141', '143', '161', '163', '1141',
        '1211', '1221', '1222', '1223',
        '1231', '1241', '1251', '1252',
        '1253', '1254', '1256', '1257',
        '1411', '1412', '1432', '1612',
        '1631', '1632', '1633', '1641',
        '1651', '1711'
    ]

    lucol = 'lulc_cls'
    """

    from glass.rd       import tbl_to_obj
    from glass.sql.db   import create_db
    from glass.it.db    import osm_to_psql
    from glass.prop.sql import cols_name
    from glass.sql.q    import exec_write_q
    from glass.it.shp   import dbtbl_to_shp

    epsg = 4326 if not epsg else epsg
    lucol = "lulccls" if not lucol or type(lucol) != str else lucol

    notags = [
        'ogc_fid', 'osm_id', 'osm_way_id', 'name', 'boundary',
        'type', 'admin_level', 'other_tags', 'wkb_geometry'
    ]

    # Import data into a database
    create_db(osm["DB"], api='psql', overwrite=True, dbset=osm["DBSET"])

    osm_to_psql(osm["FILE"], osm["DB"], dbsetup=osm["DBSET"])

    # Get multipolygon table columns
    cols = cols_name(
        osm["DB"], osm["TABLE"], dbset=osm["DBSET"],
        sanitizeSpecialWords=False
    )
    tagcols = [c for c in cols if c not in notags]

    # Get reference table
    osmtags = tbl_to_obj(reftbl["TABLE"], sheet=reftbl["SHEET"])

    # Produce Update queries
    qs = [] if lucol in cols else [(
        f"ALTER TABLE {osm['TABLE']} ADD COLUMN "
        f"{lucol} integer"
    )]

    for i, r in osmtags.iterrows():
        tags = r.osmtags.split(';')
        keys = []
        whr = []
    
        for t in tags:
            try:
                k, v = t.split('=>')
            except:
                continue
            keys.append(k)
            whr.append(f"{osm['TABLE']}.{k}='{v}'")
    
        for _t in tagcols:
            if _t not in keys:
                whr.append(f"{osm['TABLE']}.{_t} IS NULL")
    
        qs.append((
            f"UPDATE {osm['TABLE']} SET {lucol}="
            f"{str(r[reftbl['LULC_COL']])} "
            f"WHERE {' AND '.join(whr)}"
        ))
    
    # RUN queries
    exec_write_q(osm["DB"], qs, api='psql', dbset=osm["DBSET"])

    # Export data
    whr = " OR ".join([f"{lucol}={c}" for c in lucls])

    q = (
        f'SELECT ogc_fid, osm_id, name, {lucol}, '
        'building, amenity, landuse, '
        f'ST_Transform(wkb_geometry, {str(epsg)}) AS geom '
        f'FROM {osm["TABLE"]} '
        f'WHERE {whr}'
    )

    try:
        dbtbl_to_shp(
            osm["DB"], q, 'geom', oshp,
            tableIsQuery=True, api='pgsql2shp', epsg=epsg,
            dbset=osm["DBSET"]
        )
    except:
        print('No data to export from PostgreSQL')

        return None

    return oshp

