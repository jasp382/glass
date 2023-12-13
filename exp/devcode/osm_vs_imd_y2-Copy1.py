""" 
This program compare selected OSM data in Portugal with high-resolution-layers (imperviousness density maps) from Copernicus.
The objectiv is:
- Create a fishnet whit 10m, same cellsize of idm;
- Extract data from OSM and create a data base
- Intersect OSM data with fishnet;
- Insert the value of the OSM area in the fishnet cell
- Export shapefile and raster all information of this iterate 
"""     


def osm_vs_imd(osmxlsx, osmxml, imd, outfishnet, outshp):  
    
    #Create a fishnet use raster file

    from glass.smp.fish import nfishnet_fm_rst
    #fishnet = nfishnet_fm_rst(imd, 500, 500, outfishnet)

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
    import pandas as pd
    import numpy as np
    import glob

    from glass.it.osm import osm_to_psql
    from glass.it.shp import dbtbl_to_shp
    from glass.wenv.grs import run_grass
    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    from glass.prop.sql import cols_name
    from glass.rd import tbl_to_obj
    from glass.sql.q import exec_write_q
    from glass.sql.db import create_pgdb
    from glass.pys.oss import mkdir, fprop

    # Prepare workspace
    ws = mkdir(os.path.join(
        os.path.dirname(outshp), 'grswork'
    ), overwrite=True)

    #when have data in the workspace, for don't run all code again

    #ws = os.path.join(os.path.dirname(outshp), 'grswork')

    # Import data into a database
    create_pgdb(osmdata["DB"], api='psql', overwrite=True, dbset=osmdata["DBSET"])

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

    # RUN queries
    exec_write_q(osmdata["DB"], qs, api='psql', dbset=osmdata["DBSET"])

    # Export shapefile with data
    whr = " OR ".join([f"lulc_cls={c}" for c in ref_edificado])

    q = (
        f'SELECT ogc_fid, osm_id, name, lulc_cls, '
        'building, amenity, landuse, '
        f'ST_Transform(wkb_geometry, {str(epsg)}) AS geom '
        f'FROM {osmdata["TABLE"]} '
        f'WHERE {whr}'
    )

    osmlulc = dbtbl_to_shp(
        osmdata["DB"], q, 'geom', os.path.join(ws, 'osmlulc.shp'),
        tableIsQuery=True, api='pgsql2shp', epsg=epsg,
        dbset=osmdata["DBSET"]
    )

    # Start GRASS GIS Session
    loc = 'locwork'
    gb = run_grass(ws, location=loc, srs=imd)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    # GRASS GIS Modules
    from glass.it.shp import shp_to_grs, grs_to_shp
    from glass.it.rst import rst_to_grs
    from glass.gp.gen import dissolve
    from glass.tbl.col import add_fields
    from glass.tbl.grs import cols_calc
    from glass.gp.ovl.grs import grsintersection
    from glass.smp.pnt import sample_to_points

    # Import data

    osmlulcgrs = shp_to_grs(osmlulc, fprop(osmlulc, 'fn'), filterByReg=True)

    # Dissolve osm shp atraves de um atributo com valores iguais
    
    add_fields(osmlulcgrs, {'gencol': 'integer'}, api="grass")

    cols_calc(osmlulcgrs, "gencol", 1, "gencol IS NULL", ascmd=None)

    osmdiss = dissolve(osmlulcgrs, 'osmdissolve', "gencol", api='grass')

    #Loop for import all fishnet shp data
    fishnet = glob.glob(os.path.join(outfishnet,'*.shp'))

    for fileName in fishnet:
    
        fishnetgrs = shp_to_grs(fileName, fprop(fileName, 'fn'))

    # Intersect all fishnet feactures with all osm polygons

    for file in fishnet:
        t = (os.path.basename(os.path.splitext(file)[0]))
    
        iosm_fish = grsintersection(t, osmdiss, f'intersect_{t}')
   
    
        # Export intersection result to file

        ishp = grs_to_shp(iosm_fish, os.path.join(ws, iosm_fish + '.shp'), 'area')
    
    # Extract Raster values to points


    for file2 in fishnet:
        fishnetgrs2 = (os.path.basename(os.path.splitext(file2)[0]))
    
        #Export shp with centroid value
        pshp = grs_to_shp(fishnetgrs2, os.path.join(ws, f'pnt_{fishnetgrs2}.shp'), 'centroid')

    # Extract imd Raster values to points

    fishnetgrs3 = glob.glob(os.path.join(ws, 'pnt*.shp'))

    imdgrs = rst_to_grs(imd, fprop(imd, 'fn'))

    for pshp2 in fishnetgrs3:
    
        pntgrs = shp_to_grs(pshp2, fprop(pshp2, 'fn'))

        add_fields(pntgrs, {'imdval' : "double precision"}, api="grass")
    
    
        sample_to_points(pntgrs, 'imdval', imdgrs)
    
        # Export intersection result to file

        pshp = grs_to_shp(pntgrs, os.path.join(ws, f'val_{pntgrs}.shp'), 'point')

    # Open all Fishnet and Intersection results

    # Sanitize col values
    ishp2 = glob.glob(os.path.join(ws, 'intersect*.shp'))
    pshp2 = glob.glob(os.path.join(ws, 'val*.shp'))

    e = 1

    for a,b,d in zip(sorted(fishnet),sorted(ishp2),sorted(pshp2)):
    
        idf = shp_to_obj(b)
        fishdf = shp_to_obj(a)
        pdf = shp_to_obj(d)
    
    
        idf = idf[~idf.a_cat.isna()]

        idf['a_cat'] = idf.a_cat.astype(int)

        # Get field with area
        idf["garea"] = idf.geometry.area
    
        # Get area with OSM data in each cell
        areabycell = pd.DataFrame({
            'iarea' : idf.groupby(['a_cat'])['garea'].agg('sum')
            }).reset_index()
    
    
    
        # Join with original fishnet
        fishdf['cellid'] = fishdf.index + 1

        fishdf = fishdf.merge(areabycell, how='left', left_on='cellid', right_on='a_cat')
        fishdf['iarea'] = fishdf.iarea.fillna(value=0)
        fishdf["urbanp"] = fishdf.iarea * 100 / fishdf.geometry.area
    
    
    
        # Get IMD Values

        pdf.drop([c for c in pdf.columns.values if c != 'imdval'], axis=1, inplace=True)
    
        pdf['pid'] = pdf.index + 1

        fishdf = fishdf.merge(pdf, how='left', left_on="cellid", right_on="pid")
        fishdf.drop(["a_cat", "pid"], axis=1, inplace=True)
        # Export result
        if not os.path.exists(os.path.join(os.path.dirname(outshp), f'grswork{z}'))
        df_to_shp(fishdf, os.path.join(outshp,f'omsvsimd{e}.shp'))
        
        e = e+1

    #Loop for import all final result shp data

    shpfile = glob.glob(os.path.join(outshp, 'omsvs*.shp'))

    for fileName in shpfile:
        shptogrs = shp_to_grs(fileName, fprop(fileName, 'fn'))

    #All vector to raster

    from glass.it.rst import grs_to_rst
    from grass.pygrass.modules import Module
    shpfile = glob.glob(os.path.join(ws, 'omsvs*.shp'))
    a = 1
    b = 1
    for shps in sorted(shpfile):
        shape = (os.path.basename(os.path.splitext(shps)[0]))
    
        grd_rst = Module('v.to.rast', shape, output=f'gridrst{a}',
                     use='attr', attribute_column='urbanp',
                    overwrite=True)
    
        #Export grass to raster
        gridrst2 = grs_to_rst(f'gridrst{a}', (os.path.join(ws, f'osmvsimdrst{b}.tif')))
        a = a+1
        b = b+1