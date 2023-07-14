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


def join_table(shp, jshp, shpid, joinfk):
    """
    Join Tables using GRASS GIS
    """
    
    from glass.pys import execmd
    
    rcmd = execmd((
        f"v.db.join map={shp} column={shpid} "
        f"other_table={jshp} other_column={joinfk}"
    ))

    return shp


def join_attr_by_distance(mainTable, joinTable, workGrass, epsg_code,
                          output):
    """
    Find nearest feature and join attributes of the nearest feature
    to the mainTable
    
    Uses GRASS GIS to find near lines.
    """
    
    from glass.wenv.grs import run_grass
    from glass.it.pd    import df_to_geodf
    from glass.pys.oss  import fprop
    
    # Create GRASS GIS Location
    grassBase = run_grass(workGrass, location='join_loc', srs=epsg_code)
    
    import grass.script.setup as gsetup
    gsetup.init(grassBase, workGrass, 'join_loc', 'PERMANENT')
    
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
        workGrass, 'join_loc', grsMain + '_grs.shp'), None, asMultiPart=True
    ); ogrJoin = grs_to_shp(grsJoin, os.path.join(
        workGrass, 'join_loc', grsJoin + '_grs.shp'), None, asMultiPart=True)
    
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
    
    from glass.dtt.ext.toshp import shpext_to_boundshp
    from glass.dtt.torst     import shp_to_rst
    from glass.it.pd         import df_to_geodf
    from glass.wenv.grs      import run_grass
    from glass.pd.joins      import join_dfs
    from glass.pd.agg        import df_groupBy
    from glass.pys.oss       import fprop, mkdir
    
    workspace = mkdir(os.path.join(
        os.path.dirname(mainLines, 'tmp_dt')
    ))
    
    # Create boundary file
    boundary = shpext_to_boundshp(
        mainLines, os.path.join(workspace, "bound.shp"),
        epsg
    )
    
    boundRst = shp_to_rst(boundary, None, 5, -99, os.path.join(
        workspace, "rst_base.tif"), epsg=epsg, api='gdal')
    
    # Start GRASS GIS Session
    gbase = run_grass(workspace, location="grs_loc", srs=boundRst)
    
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, workspace, "grs_loc", "PERMANENT")
    
    from glass.rst.local import combine
    from glass.prop.rst  import get_rst_report_data
    from glass.it.shp    import shp_to_grs, grs_to_shp
    from glass.dtt.torst import grsshp_to_grsrst as shp_to_rst
    
    # Add data to GRASS GIS
    mainVector = shp_to_grs(
        mainLines, fprop(mainLines, 'fn', forceLower=True))
    joinVector = shp_to_grs(
        joinLines, fprop(joinLines, 'fn', forceLower=True))
    
    mainRst = shp_to_rst(mainVector, mainId, f"rst_{mainVector}")
    joinRst = shp_to_rst(joinVector, joinCol, f"rst_{joinVector}")
    
    combRst = combine(mainRst, joinRst, "combine_rst", api="pygrass")
    
    combine_data = get_rst_report_data(combRst, UNITS="c")
    
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

def join_shp_with_tbl(shp, shp_pk, tbl, tbl_fk, outShp,
                        joinFieldsMantain=None,
                        newNames=None, csv_delimiter=';', isbgri=None,
                        sheet=None, _how='inner', norelval=None):
    """
    Join BGRI ESRI Shapefile with table in xlsx or csv formats
    """
    
    from glass.pys import obj_to_lst
    
    # Read main_table
    mainDf = shp_to_obj(shp)
    
    # Read join table
    joinDf = tbl_to_obj(
        tbl, _delimiter=csv_delimiter,
        encoding_='utf-8', sheet=sheet
    )

    # Check if shp_pk is index
    if shp_pk == "index":
        mainDf["shp_pk"] = mainDf.index + 1
        shp_pk = "shp_pk"

    # Force ids to strings
    mainDf[shp_pk] = mainDf[shp_pk].astype(str)
    joinDf[tbl_fk] = joinDf[tbl_fk].astype(str)
    
    # Sanitize GEO_COD of bgriCsv
    if isbgri:
        joinDf[tbl_fk] = joinDf[tbl_fk].str.replace("'", "")
    
    if joinFieldsMantain:
        joinFieldsMantain = obj_to_lst(joinFieldsMantain)
        
        dropCols = []
        for col in joinDf.columns.values:
            if col not in [shp_pk] + joinFieldsMantain:
                dropCols.append(col)
        
        joinDf.drop(dropCols, axis=1, inplace=True)
    
    # Force numeric columns to be numeric
    for c in joinDf.columns.values:
        if c != tbl_fk:
            joinDf[c] = pd.to_numeric(joinDf[c], errors='ignore')
    
    resultDf = mainDf.merge(
        joinDf, how=_how, left_on=shp_pk, right_on=tbl_fk
    )

    if newNames:
        newNames = obj_to_lst(newNames)
        renDict = {
            joinFieldsMantain[n] : newNames[n] for n in range(len(joinFieldsMantain))
        }
        
        resultDf.rename(columns=renDict, inplace=True)
    
    # Replace Nan
    if norelval != None:
        resultDf[tbl_fk] = resultDf[tbl_fk].fillna(norelval)
    
    df_to_shp(resultDf, outShp)
    
    return outShp


def loop_join_shp_tbl(mfolder, shpname, tblname, shp_pk, tbl_fk, oname):
    """
    Run join_shp_with_tbl in a loop for the files on each sub-folder
    of a main folder
    """

    from glass.pys.oss import lst_fld

    folders = lst_fld(mfolder)

    for f in folders:
        join_shp_with_tbl(
            os.path.join(f, shpname), shp_pk,
            os.path.join(f, tblname), tbl_fk,
            os.path.join(f, oname),
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
        outt = join_shp_with_tbl(
            os.path.join(fa, r.atbl), apk,
            os.path.join(fb, r.btbl), bfk,
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


def join_xls_table(main_table, fid_main, join_table, fid_join, copy_fields, out_table,
                   main_sheet=None, join_sheet=None):
    """
    Join tables using a commum attribute
    
    Relations:
    - 1 to 1
    - N to 1
    
    TODO: Use Pandas Instead
    """
    
    import xlwt
    from glass.tbl.xls.fld import col_name
    
    copy_fields = [copy_fields] if type(copy_fields) == str else \
        copy_fields if type(copy_fields) == list else None
    
    if not copy_fields:
        raise ValueError(
            'copy_fields should be a list or a string'
        )
    
    # main_table to dict
    mainData = tbl_to_obj(
        main_table, sheet=main_sheet, useFirstColAsIndex=True, output='dict'
    )
    
    # join table to dict
    joinData = tbl_to_obj(
        join_table, sheet=join_sheet, useFirstColAsIndex=True, output='dict'
    )
    
    # write output data
    out_sheet_name = 'data' if not main_sheet and not join_sheet else join_sheet \
        if join_sheet and not main_sheet else main_sheet
    
    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(out_sheet_name)
    
    # Write tiles
    COLUMNS_ORDER = col_name(main_table, sheet_name=main_sheet)
    
    TITLES = COLUMNS_ORDER + copy_fields
    for i in range(len(TITLES)):
        new_sheet.write(0, i, TITLES[i])
    
    # parse data
    l = 1
    for fid in mainData:
        new_sheet.write(l, 0, fid)
        
        c = 1
        for col in COLUMNS_ORDER[1:]:
            new_sheet.write(l, c, mainData[fid][col])
            c+=1
        
        for col in copy_fields:
            if fid in joinData:
                new_sheet.write(l, c, joinData[fid][col])
            c+=1
        
        l += 1
    
    out_xls.save(out_table)


def join_tables_in_table(mainTable, mainIdField, joinTables, outTable):
    """
    Join one table with all tables in a folder
    
    joinTables = {
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-06.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_6'}
        },
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-13.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_13'}
        },
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-20.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_20'}
        },
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-27.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_27'}
        }
    }
    
    #TODO: only works with xlsx tables as join TABLES
    """
    
    # Get table format
    tableType = os.path.splitext(mainTable)[1]
    
    tableDf = tbl_to_obj(mainTable)
    
    for table in joinTables:
        xlsDf = tbl_to_obj(table)
        
        join_field = 'id_entity' if joinTables[table]["JOIN_FIELD"] == mainIdField \
            else joinTables[table]["JOIN_FIELD"]
        
        if joinTables[table]["JOIN_FIELD"] == mainIdField:
            xlsDf.rename(columns={mainIdField : join_field}, inplace=True)
        
        xlsDf.rename(columns=joinTables[table]["COLS_TO_JOIN"], inplace=True)
        
        tableDf = tableDf.merge(
            xlsDf, how='outer', left_on=mainIdField,
            right_on=join_field
        )
        
        tableDf.fillna(0, inplace=True)
        tableDf[mainIdField].replace(0, tableDf[join_field], inplace=True)
        
        tableDf.drop(join_field, axis=1, inplace=True)
    
    obj_to_tbl(tableDf, outTable)
    
    return outTable


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

    shpdf = shp_to_obj(shp)

    jshpdf = shp_to_obj(jshp)

    xlsdf = tbl_to_obj(auxtbl, sheet=auxsheet)

    jshpcols = list(jshpdf.columns.values)

    rdf = {fk: 'jtblfid'}
    jcols = ['jtblfid']

    for i, r in xlsdf.iterrows():
        if r[old_names] in jshpcols:
            rdf[r[old_names]] = r[new_names]
        
            jcols.append(r[new_names])

    jshpdf.rename(columns=rdf, inplace=True)
    dcols = [c for c in jshpdf.columns.values if c not in jcols]
    jshpdf.drop(dcols, axis=1, inplace=True)

    shpdf = shpdf.merge(jshpdf, how='left', left_on=pk, right_on='jtblfid')

    df_to_shp(shpdf, oshp)

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

