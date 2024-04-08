"""
Generate Reference data for Automatic OSM Classification
"""

import os
import numpy as np


def reflc_from_lcmap(objects, reflc, refrst, res, objlyr=None, outlyr=None, expbin=None):
    """
    Generate reference data from existing Land Cover map

    reflc = {
        '/path/data/source.tif : {
            'class_name' : [raster_value1, raster_value2]
            'class_name2' : [raster_valueA, raster_valueB]
        }
        '/path/data/source.shp : {
            'class_name'  : 'name_column_class_values' (binary)
            'class_name2' : 'name_column_class_values' (binary)
        }
    }
    """

    from glass.pys.oss       import mkdir, fprop
    from glass.pys.tm        import now_as_str
    from glass.wenv.grs      import grass_session
    from glass.rd.shp        import shp_to_obj
    from glass.wt.shp        import df_to_shp
    from glass.prop.df       import is_rst
    from glass.dtt.rst.torst import grsshp_to_grsrst

    ws = mkdir(os.path.join(os.path.dirname(res), f"reflc_{now_as_str()}"), overwrite=True)

    gp = grass_session(ws, loc='loc_grs', srs=refrst)

    from glass.it.rst       import rst_to_grs, grs_to_rst
    from glass.it.shp       import shp_to_grs, grs_to_shp
    from glass.rst.rcls.grs import grs_rcls, rcls_rules
    from glass.rst.zon.grs  import grs_rst_stats_by_feat

    # Import LULC rasters and Shapes
    binrsts = []
    rclssrc = {}
    for src in reflc:
        if is_rst(src):
            glc = rst_to_grs(src)

            rclssrc[glc] = reflc[src]
        
        else:
            if '.gdb' in src:
                isrc = os.path.dirname(src)
                geolyr = os.path.basename(src)

                if isrc[-4:] != '.gdb':
                    isrc = os.path.dirname(isrc)
            
            else:
                isrc, geolyr = src, None

            gvec = shp_to_grs(isrc, lyrname=geolyr)

            # Convert to raster
            for cls in reflc[src]:
                glcbin = grsshp_to_grsrst(
                    gvec, reflc[src][cls],
                    f'{gvec}_{cls}',
                    cmd=True
                )

                binrsts.append(glcbin)

    # Import objects
    gobj = shp_to_grs(objects, lyrname=objlyr)

    rules = {}

    for grst in rclssrc:
        for cls in rclssrc[grst]:
            # Reclassify
            rules = rcls_rules({
                " ".join(map(str, rclssrc[grst][cls])) : 1,
                "*" : 0 
            }, os.path.join(ws, f'rrules{grst}_{cls}.txt'))

            rclsrst = grs_rcls(grst, rules, f'rcls{grst}_{cls}', as_cmd=True)

            binrsts.append(rclsrst)

    # Get statistics of all references
    for rst in binrsts:
        grs_rst_stats_by_feat(gobj, rst, rst, ['number', 'null_cells', 'sum'], as_cmd=True)
    
    # Export objects
    oname = fprop(res, 'fn')
    tmp_gpkg = grs_to_shp(gobj, os.path.join(ws, f'{oname}.gpkg'), 'area', lname=oname)

    gdf = shp_to_obj(tmp_gpkg, lyr=oname)

    gdf['geom_area'] = gdf.geometry.area

    gdf = gdf[gdf.geom_area >= 1000]

    #rename_cols = {'ref_null_cells' : 'ref_null'}
    for rst in binrsts:
        gdf[f'{rst}_sum'] = gdf[f'{rst}_sum'].fillna(value=0)
        gdf[f'{rst}_sum'] = gdf[f'{rst}_sum'].astype(float)
        gdf[f'{rst}_p']   = gdf[f'{rst}_sum'] / gdf[f'{rst}_number'] * 100

        gdf[rst] = np.where(
            gdf[f'{rst}_p'] >= 20, 1, -1 
        )

        gdf[rst] = np.where(
            (gdf[f'{rst}_sum'] == 0) & (gdf[f'{rst}_null_cells'] == 0),
            0, gdf[rst]
        )

        #rename_cols[f'{k}_sum'] = f'{k[:5]}_sum'
        #rename_cols[f'{k}_p'] = f'{k[:5]}_p'
        #rename_cols[k] = k[:5]

    #gdf.rename(columns=rename_cols, inplace=True)

    # Save result
    df_to_shp(gdf, res, layername=outlyr)

    # Export binary rasters is requested
    if expbin:
        for r in binrsts:
            grs_to_rst(
                r, os.path.join(os.path.dirname(res), f"{r}.tif"),
                dtype='Byte', nodata=2
            )

    return res



def reflc_of_obj(gpkg, areaname, pk, files_classes, outlyr, ofolder, outbymap=None, outbyclass=None):
    """
    """

    from glass.pys.oss import fprop

    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    gdf = shp_to_obj(gpkg, lyr=fprop(gpkg, 'fn'))

    clscols, icols = {}, [pk, 'geometry']

    for file in files_classes:
        for cls in files_classes[file]:
            col = f'rcls{file}_{areaname}_{cls}'
            icols.append(col)

            if cls not in clscols:
                clscols[cls] = [col]

            else:
                clscols[cls].append(col)
            
            # Create a file for each class and map
            _gdf = gdf.copy(deep=True)

            _gdf = _gdf[[pk, 'geometry', col]]

            _gdf.rename(columns={col : cls}, inplace=True)

            _gdf = _gdf[_gdf[cls] > -1]

            df_to_shp(_gdf, os.path.join(
                ofolder if not outbymap else outbymap, 
                f'{file}_{cls}_{areaname}.shp'
            ))

    gdf = gdf[icols]

    drop = []
    for cls in clscols:
        gdf[cls] = gdf[clscols[cls][0]]

        drop.append(clscols[cls][0])

        if len(clscols[cls]) == 1:
            continue

        for i in range(1, len(clscols[cls])):
            gdf[cls] = np.where(
                gdf[cls] == gdf[clscols[cls][i]],
                gdf[cls], -1
            )

            drop.append(clscols[cls][i])

    gdf.drop(drop, axis=1, inplace=True)

    # Save result in the same geopackage
    df_to_shp(gdf, os.path.join(ofolder, f'{outlyr}.shp'))

    # Create a file for each class
    ofiles = []
    for cls in clscols:
        fdf = gdf[gdf[cls] > -1]

        ofile = os.path.join(
            ofolder if not outbyclass else outbyclass,
            f'ref_{cls}_{areaname}.shp'
        )

        df_to_shp(fdf, ofile)

        ofiles.append(ofile)

    
    return ofiles

