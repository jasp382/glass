"""
Automatic classification of OSM Data
"""

import pandas as pd
import numpy as np




def tags_to_text(ref_objs, osm_data, tags, out_text, geoexp=True, poly50p=True, excludebuildyes=None):
    """
    OSM Tags to Text

    Inputs example:


    ref_objs = {
        'path'  : 'X://autoclsosm_tk1/artificial_cmb/class_objs.shp',
        'pkcol' :  'objid',
        'refclass' : None
    }

    osm_data = {
        'polygons' : {
            'path' : 'X://autoclsosm_tk1/artificial_cmb/class_poly.shp',
            'fkcol' : 'objid'
        }, 
        'lines'    : {
            'path' : 'X://autoclsosm_tk1/artificial_cmb/class_lnh.shp',
            'fkcol' : 'objid'
        },
        'points'   : {
            'path' : 'X://autoclsosm_tk1/artificial_cmb/class_pnt.shp',
            'fkcol' : 'objid'
        }
    }

    tags = [
        'aeroway', 'amenity', 'building', 'craft',
        'geological', 'historic', 'landuse', 'leisure', 'man_made',
        'military', 'natural', 'office', 'place', 'shop', 'sport', 'tourism',
        'waterway', 'power', 'railway', 'healthcare', 'highway', 'water',
        'landcover', 'industrial', 'leaf_type', 'material', 'surface',
        'leaf_cycle', 'cuisine', 'religion'
    ]

    out_text = 'X://autoclsosm_tk1/artificial_cmb/class_osmtext.xlsx'
    """

    import copy

    from glass.rd.shp     import shp_to_obj
    from glass.dtt.mge.pd import merge_df
    from glass.wt         import obj_to_tbl

    osmd = copy.deepcopy(osm_data)

    df_obj = shp_to_obj(ref_objs['path'])

    df_obj["tarea"] = df_obj.geometry.area
    df_obj["pp"]    = df_obj.geometry.length

    df_osm = {}
    for k in osmd:
        df_osm[k] = shp_to_obj(osmd[k]['path'])

        if ref_objs['pkcol'] == osmd[k]['fkcol']:
            fk = f'{osmd[k]["fkcol"]}_fk'

            df_osm[k].rename(columns={osmd[k]['fkcol'] : fk}, inplace=True)

            osmd[k]['fkcol'] = fk
    
        # Get geographic expression
        if geoexp:
            if k == 'polygons':
                df_osm[k]['iattr'] = df_osm[k].geometry.area
            elif k == 'lines':
                df_osm[k]['iattr'] = df_osm[k].geometry.length
            else:
                df_osm[k]['iattr'] = 1
        
        else:
            df_osm[k]['iattr'] = 1
        
        if not geoexp and poly50p and k == 'polygons':
            df_osm[k]['gattr'] = df_osm[k].geometry.area
        
        # Get Objects with polygon data
        if k == 'polygons' and poly50p:
            gatr = 'gattr' if not geoexp else 'iattr'
            objpoly = pd.DataFrame({
                'garea'  : df_osm[k].groupby([osmd[k]['fkcol']])[gatr].agg('sum')
            }).reset_index()

        # Delete columns
        _tags = tags + [osmd[k]['fkcol'], 'iattr']
        dc = [c for c in df_osm[k].columns.values if c not in _tags]
        df_osm[k].drop(dc, axis=1, inplace=True)
    
    # Filter objects
    # Select objects with at least 50% of area OSM polygons
    if poly50p:
        df_obj = df_obj.merge(
            objpoly, how='inner', left_on=ref_objs['pkcol'],
            right_on=osmd['polygons']['fkcol']
        )

        df_obj = df_obj[df_obj.garea / df_obj.geometry.area * 100 > 50]

        df_obj.drop([osmd['polygons']['fkcol'], 'garea'], axis=1, inplace=True)
    
    dfs = {}

    i = 1
    for k in df_osm:
        _dfs = []
        cols = df_osm[k].columns.values
        i+= 1

        # Create one dataframe for each tag
        for tag in tags:
            if tag not in cols: continue
        
            _df = df_osm[k][~pd.isna(df_osm[k][tag])]
            _df = _df[_df[tag] != '']
            _df = _df[_df[tag] != ' ']

            _dc = [c for c in cols if c != tag and \
                c != osmd[k]['fkcol'] and c != 'iattr']
            
            _df.drop(_dc, axis=1, inplace=True)

            _df['osm_key'] = tag
            _df.rename(columns={tag : 'osm_value'}, inplace=True)

            _dfs.append(_df)
        
        # Join dataframes of different tags
        nw_osm = merge_df(_dfs)

        #nw_osm['osm_text'] = k + '<=' + nw_osm.osm_key + '=>' + nw_osm.osm_value
        nw_osm['osm_text'] = nw_osm.osm_key + ' ' +  nw_osm.osm_value

        if excludebuildyes:
            nw_osm = nw_osm[nw_osm.osm_text != 'building yes']

        osmby = pd.DataFrame({
            'byattr' : nw_osm.groupby([
                osmd[k]['fkcol'],
                'osm_text'
            ])['iattr'].agg('sum')
        }).reset_index()

        # Get area and length of original objetcs
        # Calculate spatial expression
        if k == 'polygons' or k == 'lines':
            osmby = osmby.merge(
                df_obj, how='inner',
                left_on=osmd[k]['fkcol'],
                right_on=ref_objs['pkcol']
            )

            if geoexp:
                if k == 'polygons':
                    osmby['byattr'] = osmby['byattr'] / osmby['tarea'] * 100

                elif k == 'lines':
                    osmby['byattr'] = osmby['byattr'] / osmby['pp'] * 100

                osmby['byattr'] = osmby['byattr'].round(0)

                osmby['byattr'] = np.where(
                    osmby['byattr'] < 1, 1,
                    osmby['byattr']
                )

                osmby['byattr'] = osmby['byattr'].astype(int)

            od = [c for c in osmby.columns.values if c in df_obj.columns.values]
            osmby.drop(od, axis=1, inplace=True)

        # Multiply tags based on spatial expression or frequency
        osmby['osm_text'] = (osmby['osm_text'] + ' ') * osmby['byattr']

        # Group by object id
        osmby['osm_agg'] = osmby.groupby([
            osmd[k]['fkcol']
        ])['osm_text'].transform(lambda x: ' '.join(x))

        osmby.drop(['byattr', 'osm_text'], axis=1, inplace=True)

        osmby = osmby.drop_duplicates()

        osmby.rename(columns={'osm_agg' : f'txt_{k}'}, inplace=True)

        dfs[k] = osmby
    
    # Put everything in the objects table
    # Concatenate all text
    osm_text = None
    for k in dfs:
        df_obj = df_obj.merge(
            dfs[k], how='left',
            left_on=ref_objs['pkcol'],
            right_on=osmd[k]['fkcol']
        )

        df_obj[f'txt_{k}'] = np.where(
            df_obj[f'txt_{k}'].isna(),
            '', df_obj[f'txt_{k}']
        )

        if not osm_text:
            df_obj.rename(columns={f'txt_{k}' : 'osm_text'}, inplace=True)
            delc = [osmd[k]['fkcol']]

            osm_text = True

        else:
            df_obj['osm_text'] = df_obj['osm_text'] + ' ' + df_obj[f'txt_{k}']
            delc = [osmd[k]['fkcol'], f'txt_{k}']

        df_obj.drop(delc, axis=1, inplace=True)
    
    # Write output
    icols = [ref_objs['pkcol'], 'osm_text']

    if ref_objs['refclass']:
        icols.append(ref_objs['refclass'])

    dcols = [c for c in df_obj.columns.values if c not in icols]

    df_obj.drop(dcols, axis=1, inplace=True)

    owd = df_obj[df_obj.osm_text.str.len() > 2]
    ond = df_obj[df_obj.osm_text.str.len() <= 2]

    obj_to_tbl([owd, ond], out_text, sheetsName=['objstags', 'no_osm_data'])

    return out_text



def tags_to_feat(objs, obj_pk, osm_tags, osm_data, out):
    """
    OSM Tags to Text

    objs = '/mnt/x/aosm_tk3/aosmtk3.gdb/sar_refua_valencia'

    obj_pk = 'refid'

    osm_tags = {
        'table' : '/mnt/x/aosm_tk3/valencia_osm_tags.xlsx',
        'osmkey' : 'osm_key',
        'osmval' : 'osm_value'
    }

    osm_data = {
        'polygons' : {
            "shp"      : '/mnt/x/aosm_tk3/aosmtk3.gdb/refosm_valencia_ply',
            "fk"       : "refid",
            "geomprop" : "osmarea"
        },
        'lines'    : {
            "shp"      : '/mnt/x/aosm_tk3/aosmtk3.gdb/refosm_valencia_lnh',
            "fk"       : "refid",
            "geomprop" : 'osmcount'
        },
        'points'   : {
            "shp"      : '/mnt/x/aosm_tk3/aosmtk3.gdb/refosm_valencia_pnt',
            "fk"       : "refid",
            "geomprop" : 'osmcount'
        }
    }

    out = '/mnt/x/aosm_tk3/osmfeat/feat_valencia.xlsx'
    """

    return out

