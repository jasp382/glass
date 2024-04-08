"""
Custom Joins
"""

import os
import pandas as pd


from glass.rd.shp   import shp_to_obj
from glass.rd       import tbl_to_obj
from glass.wt       import obj_to_tbl
from glass.wt.shp   import df_to_shp, obj_to_shp
from glass.prop.prj import get_epsg



def join_fields(tleft, pk_left, right_tbls, out, leftSheet=None, leftDelimiter=';',
                _how='inner', norelval=None, oepsg=None):
    """
    Join tables

    right_sample = {
        '/table/path' : {
            'fk' : 'fk_col',
            'cols' : ['col_a', 'col_b'],
            'sheet' : None,
            'delimiter' : None,
            'isbgri' : None,
            'newnames' : ['col_d', 'col_c'],
            'forcenum' : True
        }
    }
    """

    from glass.prop.df import is_shp
    from glass.pys import obj_to_lst
    from glass.pys.oss import fprop
    from glass.prop.prj import df_epsg

    ioshp = is_shp(out)

    # Read main table
    ishp = is_shp(tleft)

    mdf = shp_to_obj(tleft) if ishp else tbl_to_obj(
        tleft, _delimiter=leftDelimiter,
        encoding_='utf-8', sheet=leftSheet
    )

    if not oepsg and ishp:
        oepsg = df_epsg(ishp)

    if pk_left == "index":
        mdf['fidpk'] = mdf.index + 1
        pk_left = 'fidpk'
    
    # Force PK to String
    mdf[pk_left] = mdf[pk_left].astype(str)

    # Open Right tables
    for f in right_tbls:
        rname = fprop(f, 'fn')
        ris_shp = is_shp(f)

        fk = right_tbls[f]['fk']

        dlm = ';' if "delimiter" not in right_tbls[f] else \
            right_tbls[f]["delimiter"]
        
        sht = None if "sheet" not in right_tbls[f] else \
            right_tbls[f]["sheet"]
        
        ibgri = None if "isbgri" not in right_tbls[f] else \
            right_tbls[f]["isbgri"]
        
        fnum = None if "forcenum" not in right_tbls[f] else \
            right_tbls[f]["forcenum"]
        
        newnam = None if "newnames" not in right_tbls[f] else \
            obj_to_lst(right_tbls[f]["newnames"])

        rdf = shp_to_obj(f) if ris_shp else tbl_to_obj(
            f, _delimiter=dlm, encoding_='utf-8',
            sheet=sht
        )

        if not oepsg and ris_shp and ioshp:
            oepsg = df_epsg(rdf, "geometry")

        rdf[fk] = rdf[fk].astype(str)

        if ibgri:
            rdf[fk] = rdf[fk].str.replace("'", "")

        if "cols" in right_tbls[f]:
            rcols = obj_to_lst(right_tbls[f]["cols"])

            dc = [c for c in rdf.columns.values if c not in rcols and c != fk]

            rdf.drop(dc, axis=1, inplace=True)

            if newnam and len(newnam) == len(rcols):
                rncols = {rcols[i] : newnam[i] for i in range(len(rcols))}

                rdf.rename(columns=rncols, inplace=True)

        rdf.rename(columns={fk : f"{rname}_fk"}, inplace=True)

        # Force numeric columns to be numeric
        if fnum:
            for c in rdf.columns.values:
                if c == f"{rname}_fk":
                    continue

                rdf[c] = pd.to_numeric(rdf[c], errors='ignore')

        mdf = mdf.merge(
            rdf, how=_how, left_on=pk_left,
            right_on=f"{rname}_fk"
        )

        # Replace Nan if necessary
        if norelval != None:
            for c in rdf.columns.values:
                mdf[c] = mdf[c].fillna(norelval)

        mdf.drop([f"{rname}_fk"], axis=1, inplace=True)

    obj_to_shp(mdf, 'geometry', oepsg, out) if ioshp else \
        obj_to_tbl(mdf, out)

    return out




def join_attr_by_distance(mainTable, joinTable, workGrass, epsg_code,
                          output):
    """
    Find nearest feature and join attributes of the nearest feature
    to the mainTable
    
    Uses GRASS GIS to find near lines.
    """
    
    from glass.wenv.grs import grass_session
    from glass.it.pd    import df_to_geodf
    from glass.pys.oss  import fprop
    
    # Create GRASS GIS Location
    grassBase = grass_session(workGrass, loc='join_loc', srs=epsg_code)
    
    # Import some GRASS GIS tools
    from glass.gp.prox import grs_near as near
    from glass.it.shp  import shp_to_grs, grs_to_shp
    
    # Import data into GRASS GIS
    grsMain = shp_to_grs(mainTable, fprop(
        mainTable, 'fn', forceLower=True)
    ); grsJoin = shp_to_grs(joinTable, fprop(
        joinTable, 'fn', forceLower=True)
    )
    
    # Get distance from each feature of mainTable to the nearest feature
    # of the join table
    near(grsMain, grsJoin, nearCatCol="tocat", nearDistCol="todistance")
    
    # Export data from GRASS GIS
    ogrMain = grs_to_shp(grsMain, os.path.join(
        workGrass, 'join_loc', f'{grsMain}_grs.shp'), None, asMultiPart=True
    ); ogrJoin = grs_to_shp(grsJoin, os.path.join(
        workGrass, 'join_loc', f'{grsJoin}_grs.shp'), None, asMultiPart=True)
    
    dfMain = shp_to_obj(ogrMain)
    dfJoin = shp_to_obj(ogrJoin)
    
    dfResult = dfMain.merge(dfJoin, how='inner',
                            left_on='tocat', right_on='cat')
    
    dfResult.drop(["geometry_y", "cat_y"], axis=1, inplace=True)
    dfResult.rename(columns={"cat_x" : "cat_grass"}, inplace=True)
    
    dfResult["tocat"]     = dfResult["tocat"] - 1
    dfResult["cat_grass"] = dfResult["cat_grass"] - 1
    
    dfResult = df_to_geodf(dfResult, "geometry_x", epsg_code)
    
    df_to_shp(dfResult, output)
    
    return output


def joinLines_by_spatial_rel_raster(mainLines, mainId, joinLines,
                                    joinCol, outfile, epsg):
    """
    Join Attributes based on a spatial overlap.
    An raster based approach
    """
    
    from glass.dtt.toshp import shpext_to_boundshp
    from glass.dtt.rst.torst import shp_to_rst
    from glass.it.pd     import df_to_geodf
    from glass.wenv.grs  import grass_session
    from glass.pd.joins  import join_dfs
    from glass.pd.agg    import df_groupBy
    from glass.pys.oss   import fprop, mkdir
    
    workspace = mkdir(os.path.join(
        os.path.dirname(mainLines, 'tmp_dt')
    ))
    
    # Create boundary file
    boundary = shpext_to_boundshp(
        mainLines, os.path.join(workspace, "bound.shp"),
        epsg
    )
    
    boundRst = shp_to_rst(boundary, None, 5, -99, os.path.join(
        workspace, "rst_base.tif"), epsg=epsg, api='pygdal')
    
    # Start GRASS GIS Session
    gbase = grass_session(workspace, loc="grs_loc", srs=boundRst)
    
    from glass.rst.local     import combine
    from glass.prop.rst      import san_report_combine
    from glass.it.shp        import shp_to_grs, grs_to_shp
    from glass.dtt.rst.torst import grsshp_to_grsrst as shp_to_rst
    
    # Add data to GRASS GIS
    mainVector = shp_to_grs(
        mainLines, fprop(mainLines, 'fn', forceLower=True))
    joinVector = shp_to_grs(
        joinLines, fprop(joinLines, 'fn', forceLower=True))
    
    mainRst = shp_to_rst(mainVector, mainId, f"rst_{mainVector}")
    joinRst = shp_to_rst(joinVector, joinCol, f"rst_{joinVector}")
    
    combRst = combine(mainRst, joinRst, "combine_rst", api="pygrass")
    
    combine_data = san_report_combine(combRst, UNITS="c")
    
    combDf = pd.DataFrame(combine_data, columns=[
        "comb_cat", "rst_1", "rst_2", "ncells"
    ])
    combDf = combDf[combDf["rst_2"] != '0']
    combDf["ncells"] = combDf["ncells"].astype(int)
    
    gbdata = df_groupBy(combDf, ["rst_1"], "MAX", "ncells")
    
    fTable = join_dfs(gbdata, combDf, ["rst_1", "ncells"], ["rst_1", "ncells"])
    
    fTable["rst_2"] = fTable["rst_2"].astype(int)
    fTable = df_groupBy(
        fTable, ["rst_1", "ncells"],
        STAT='MIN', STAT_FIELD="rst_2"
    )
    
    mainLinesCat = grs_to_shp(
        mainVector, os.path.join(workspace, mainVector + '.shp'), 'line')
    
    mainLinesDf = shp_to_obj(mainLinesCat)
    
    resultDf = join_dfs(
        mainLinesDf, fTable, "cat", "rst_1",
        onlyCombinations=None
    )
    
    resultDf.rename(columns={"rst_2" : joinCol}, inplace=True)
    
    resultDf = df_to_geodf(resultDf, "geometry", epsg)
    
    df_to_shp(resultDf, outfile)
    
    return outfile


"""
Do Joins and stuff with excel tables
"""


def loop_join_shp_tbl(mfolder, shpname, tblname, shp_pk, tbl_fk, oname):
    """
    Run join_shp_with_tbl in a loop for the files on each sub-folder
    of a main folder
    """

    from glass.pys.oss import lst_fld

    folders = lst_fld(mfolder)

    for f in folders:
        right_ = {
            os.path.join(f, tblname) : {'fk' : tbl_fk}
        }
        join_fields(
            os.path.join(f, shpname), shp_pk,
            right_, os.path.join(f, oname),
            _how="left", norelval=-1
        )


def loop_join_shp_tbl_sameid(fa, fb, of, apk, bfk, oname, tbff='.dbf'):
    """
    List files in two folders, get id from file name, join tables
    with same id
    """

    from glass.pys.oss import lst_ff, lst_fld, mkdir

    fld = lst_fld(os.path.dirname(of), name=True)

    if os.path.basename(of) not in fld:
        mkdir(of, overwrite=False)

    # List tables in folder a
    # assuming file id is the last part of the filename
    # {filename}_{id}.shp
    # id must be an integer

    a_tbl = pd.DataFrame([{
        'aid'  : int(f.split('.')[0].split('_')[-1]),
        'atbl' : f
    } for f in lst_ff(
        fa, rfilename=True, file_format='.shp'
    )])

    # List tables in folder b
    b_tbl = pd.DataFrame([{
        'bid'  : int(f.split('.')[0].split('_')[-1]),
        'btbl' : f
    } for f in lst_ff(
        fb, rfilename=True, file_format=tbff
    )])

    # Join two dataframes
    jt = a_tbl.merge(b_tbl, how='inner', left_on='aid', right_on='bid')

    # Join tables
    ot = []
    for i, r in jt.iterrows():
        right_ = {
            os.path.join(fb, r.btbl) : {'fk' : bfk}
        }
        outt = join_fields(
            os.path.join(fa, r.atbl), apk,
            right_,
            os.path.join(of, f"{oname}_{str(r.aid)}.shp"),
            _how="left", norelval=-1
        )

        ot.append(outt)

    return ot


def calc_mean_samecol_sevshp(intbls, pk, meancol, output, tformat='.shp'):
    """
    Calculate mean of the same column in different tables

    Assume we have N tables with a numerical column with the same name

    This script calculate the mean of all these columns
    """

    if os.path.isdir(intbls):
        from glass.pys.oss import lst_ff

        tbls = lst_ff(intbls, file_format='.shp' if not tformat else tformat)
    
    else:
        if type(intbls) == list:
            tbls = intbls
        else:
            raise ValueError('intbls has an invalid value')
    
    # Read data
    dfs = [shp_to_obj(t) for t in tbls]

    # Drop uncessary cols
    mantain_cols = [pk, meancol]
    for d in range(len(dfs)):
        dfs[d].drop([
            c for c in dfs[d].columns.values if c not in mantain_cols
        ], axis=1, inplace=True)

        if d:
            dfs[d].rename(columns={
                pk      : f"{pk}_{str(d)}",
                meancol : f"{meancol}_{str(d)}"
            }, inplace=True)
    
    # Join all DFS
    main_df = dfs[0]

    for d in range(1, len(dfs)):
        main_df = main_df.merge(
            dfs[d], how='outer', left_on=pk,
            right_on=f"{pk}_{str(d)}"
        )

        main_df[meancol] = main_df[meancol] + main_df[meancol + "_" + str(d)]
    
    # Get mean
    main_df[meancol] = main_df[meancol] / len(dfs)

    # Drop uncessary cols
    drop_cols = []
    for d in range(1, len(dfs)):
        drop_cols.append(f"{pk}_{str(d)}")
        drop_cols.append(f"{meancol}_{str(d)}")
    
    main_df.drop(drop_cols, axis=1, inplace=True)

    # Export Result
    obj_to_tbl(main_df, output)

    return output


def field_sum_two_tables(tableOne, tableTwo,
                         joinFieldOne, joinFieldTwo,
                         field_to_sum, outTable):
    """
    Sum same field in different tables
    
    Table 1:
    id | field
    0 |  10
    1 |  11
    2 |  13
    3 |  10
    
    Table 2:
    id | field
    0 |  10
    1 |   9
    2 |  17
    4 |  15
    
    Create the new table
    id | field
    0 |  20
    1 |  20
    2 |  30
    3 |  10
    4 |  15
    """
    
    from glass.pd.joins import sum_field_of_two_tables
    
    # Open two tables
    df_one = tbl_to_obj(tableOne)
    df_two = tbl_to_obj(tableTwo)
    
    # Do it!
    outDf = sum_field_of_two_tables(
        df_one, joinFieldOne,
        df_two, joinFieldTwo,
        field_to_sum
    )
    
    obj_to_tbl(outDf, outTable)
    
    return outTable


def field_sum_by_table_folder(folderOne, joinFieldOne,
                              folderTwo, joinFieldTwo,
                              sum_field, outFolder):
    
    from glass.pys.oss import lst_ff, fprop
    
    tablesOne = lst_ff(folderOne, file_format=['.xls', '.xlsx'])
    tablesTwo = lst_ff(folderTwo, file_format=['.xls', '.xlsx'])
    
    for table in tablesOne:
        table_name = fprop(table, 'fn')
        
        for __table in tablesTwo:
            __table_name = fprop(__table, 'fn')
            
            if table_name == __table_name:
                field_sum_two_tables(
                    table, __table, joinFieldOne, joinFieldTwo, sum_field,
                    os.path.join(outFolder, os.path.basename(table))
                )
                
                break


def rows_tbla_notin_tblb(ta, tb, pka, pkb, out):
    """
    Get records of Table A not in Table B
    """

    epsg = get_epsg(ta)

    # Open Shapes
    dfa = shp_to_obj(ta)
    dfb = shp_to_obj(tb)

    # Rename all columns in table_b
    cols = {c : f"b_{c}" for c in dfb.columns.values}
    dfb.rename(columns=cols, inplace=True)
    pkb = f"b_{pkb}"

    # Join
    res = dfa.merge(dfb, how='left', left_on=pka, right_on=pkb)

    # Get no relation records
    res = res[res[pkb].isna()]

    # Delete unecessary cols
    res.drop(list(cols.values()), axis=1, inplace=True)

    # Write result
    obj_to_shp(res, 'geometry', epsg, out)

    return out


def copy_fields_based_on_table(shp, jshp, pk, fk, auxtbl, auxsheet,
                               old_names, new_names, oshp):
    """
    Copy fields from one shape to another and rename the fields
    based on another table
    """

    xlsdf = tbl_to_obj(auxtbl, sheet=auxsheet)

    cols = xlsdf[old_names].tolist()
    new  = xlsdf[new_names].tolist()

    right_ = {
        jshp : {'fk' : fk, 'cols' : cols, 'newnames' : new}
    }

    join_fields(
        shp, pk, right_,
        oshp, _how='left'
    )

    return oshp


def nton_to_table(left_t, right_t, right_sheet, rel_t, rel_sheet, otable,
                  left_pk, left_fk, right_pk, right_fk):
    """
    N-TO-N Relation to single table
    """

    epsg = get_epsg(left_t)

    left_df = shp_to_obj(left_t)

    right_df = tbl_to_obj(right_t, sheet=right_sheet)

    rel_df = tbl_to_obj(rel_t, rel_sheet)

    # Join rel with right
    rel_df = rel_df.merge(
        right_df, how='inner',
        left_on=right_fk, right_on=right_pk
    )

    # Join freg with data
    left_df = left_df.merge(
        rel_df, how='left',
        left_on=left_pk, right_on=left_fk
    )

    obj_to_shp(left_df, 'geometry', epsg, otable)

    return otable

