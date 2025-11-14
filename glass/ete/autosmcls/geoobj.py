"""
Geo-Objects classification
"""

def pg_calc_geo_objects(bgri, osm, water, odb, final_objects, outdump=None,
                        out_gpkg=None, out_shp=None, gen_touch=None, msbuild=None, min_area=1000):
    """
    Generate Geo-Objects
    """

    from glass.cons.otol    import tags_module2_and5
    from glass.ete.otol.vec import osmlines_buffer
    from glass.gp.gen.sql   import st_diss_adjacentpoly
    from glass.gp.ovl.sql   import st_pgerase, st_touching, st_pgleft_union
    from glass.gp.seg.sql   import geomseg_to_newtbl
    from glass.it.db        import osm_to_psql
    from glass.sql.db       import create_pgdb
    from glass.it.db        import shp_to_psql
    from glass.prop.prj     import get_epsg
    from glass.sql.q        import exec_write_q

    # Get EPSG
    epsg = get_epsg(bgri)

    # Create PG Database
    create_pgdb(odb, overwrite=True)

    # Import OSM data
    osm_to_psql(osm, odb)

    # Import BGRI Data and Water Bodies
    # Import MS building footpring Aggregated result if given
    shps = [bgri, water]
    if msbuild:
        shps.append(msbuild)
    
    impres = shp_to_psql(odb, shps, api='ogr2ogr')

    if not msbuild:
        impres.append(None)
    
    bgri_tbl, water_tbl, msbuild_tbl = impres

    # Generate OSM Lines theme
    mod_tags = tags_module2_and5('uatlas')

    roads_tbl, meta = osmlines_buffer(odb, mod_tags, epsg, None, 'linesbuffer')
    uproads_qs = [(
        f"ALTER TABLE {roads_tbl} ADD CONSTRAINT "
        f"{roads_tbl}_pk PRIMARY KEY (lulc)"
    ), (
        f"CREATE INDEX {roads_tbl}_geom_idx ON "
        f"{roads_tbl} USING gist (geometry)"
    )]

    exec_write_q(odb, uproads_qs, api='psql')

    # Union BGRI and MSBuilds if exist
    if msbuild_tbl:
        bgri_tbl = st_pgleft_union(
            odb, bgri_tbl, msbuild_tbl,
            'ogc_fid', "geom", "geom",
            out=f"{bgri_tbl}_msb"
        )

    # Subdivide water bodies and roads
    _water_tbl = geomseg_to_newtbl(
        odb, water_tbl, 'ogc_fid', 'geom',
        'polygon', epsg, f'{water_tbl}_v2',
        subdivide_factor=10
    )

    _roads_tbl = geomseg_to_newtbl(
        odb, roads_tbl, 'lulc', 'geometry',
        'polygon', epsg, f'{roads_tbl}_v2',
        subdivide_factor=10
    )

    # Erase roads
    bgri_v2 = st_pgerase(
        odb, bgri_tbl, 'ogc_fid',
        _roads_tbl, "geom", "geom",
        otbl="objects_v1"
    )

    # Erase water
    bgri_v3 = st_pgerase(
        odb, bgri_v2, 'ogc_fid',
        _water_tbl, "geom", "geom",
        otbl="objects_v2"
    )

    if gen_touch:
        st_touching(
            odb, bgri_v3, "geom",
            bgri_v3, "geom",
            otbl="testetouch",
            bcols='ogc_fid AS b_fid',
            awhr=f"ST_Area(geom) > {str(min_area)}",
            bwhr=f"ST_Area(geom) < {str(min_area)}"
        )

    # Dissolve adjancent polygons
    bgri_v4 = st_diss_adjacentpoly(
        odb, bgri_v3, 'ogc_fid', 'geom',
        otbl=final_objects,
        areathreshold=min_area,
        dissrule='length'
    )

    if out_gpkg:
        from glass.it.shp import db_to_gpkg

        db_to_gpkg(odb, out_gpkg)
    
    if outdump:
        from glass.sql.bkup import dump_db

        dump_db(odb, outdump, api='psql')
    
    if out_shp:
        from glass.it.shp import dbtbl_to_shp

        dbtbl_to_shp(odb, bgri_v4, 'geom', out_shp, api='psql')

    return bgri_v4, out_gpkg if out_gpkg else odb

