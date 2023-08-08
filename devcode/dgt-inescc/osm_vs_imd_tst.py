def osm_vs_imd(osmxlsx, osmxml, imd, outfishnet, outshp):  
    
    #Create a fishnet use raster file
    while imd:
        
        osm_ref_tags = {
            
            "TABLE"     : osmxlsx,
            "SHEET"     : 'osm_features',
            "LULC_COL"  : 'L4',
            "KEY_COL"   : "key",
            "VALUE_COL" : "value",
            "GEOM_COL"  : "geom"
            }

        osmdata = {
            "FILE"  : osmxml,
            "DB"    : 'dgt_cmb',
            "TABLE" : "multipolygons",
            "DBSET" : "local"
            }

        ref_edificado = [
            '1151', '1221',
            '1222', '1223', '1231', '1241',
            '1251', '1252', '1254', '1255',
            '1257', '1253', '1612',
            '1631', '1632', '1633', '1651',
            '16', '143', '1431', '1432'
            ]


        lulccls = 'lulc_cls' 

        epsg = 3763    
    
        import os

        from glass.it.osm import osm_to_psql

        from glass.prop.sql import cols_name
        from glass.rd import tbl_to_obj
        from glass.sql.db import create_db
        from glass.pys.oss import mkdir

        # Prepare workspace
        ws = mkdir(os.path.join(
            os.path.dirname(outshp), 'grswork'
        ), overwrite=True)

    #when have data in the workspace, for don't run all code again

    #ws = os.path.join(os.path.dirname(outshp), 'grswork')

    # Import data into a database
        create_db(osmdata["DB"], api='psql', overwrite=True, dbset=osmdata["DBSET"])

        osm_to_psql(osmdata["FILE"], osmdata["DB"])
    

        osm_tags = tbl_to_obj(osm_ref_tags["TABLE"], sheet=osm_ref_tags["SHEET"])

        osm_tags = osm_tags[osm_tags[osm_ref_tags["GEOM_COL"]] == 'Polygon']
    
        osm_tags['sevtags'] = osm_tags[osm_ref_tags["LULC_COL"]].str.contains(';')

        osm_tags = osm_tags[osm_tags.sevtags != True]

    # Create key/value column
        osm_tags.loc[:, osm_ref_tags["VALUE_COL"]] = osmdata["TABLE"] + "." + \
            osm_tags[osm_ref_tags["KEY_COL"]] + \
            "='" + osm_tags[osm_ref_tags["VALUE_COL"]] + "'"

    # Add new column to multipolygons table
    # Update it adding an LULC class

        cols = cols_name(osmdata["DB"], osmdata['TABLE'], dbset=osmdata["DBSET"])

        qs = [] if "lulc_cls" in cols else [(
            f"ALTER TABLE {osmdata['TABLE']} ADD COLUMN "
            "lulc_cls integer"
        )]

        for cls in osm_tags[osm_ref_tags["LULC_COL"]].unique():
    # Se uma feature estiver associada a duas TAGS que dizem respeito a classes
    # diferentes, a classe da feature será a última classe considerada
    # Abordagem multitag vai resolver este problema.
            __osmtags = osm_tags[osm_tags[osm_ref_tags["LULC_COL"]] == cls]
    
            qs.append((
                f"UPDATE {osmdata['TABLE']} SET lulc_cls={str(cls)} "
                f"WHERE {str(__osmtags[osm_ref_tags['VALUE_COL']].str.cat(sep=' OR '))}"
            ))

        cols = cols_name(osmdata["DB"], osmdata['TABLE'], dbset=osmdata["DBSET"])
        print(cols)