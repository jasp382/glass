"""
Custom Joins with GRASS GIS
"""

def join_table(inShp, jnTable, shpCol, joinCol):
    """
    Join Tables GRASS GIS
    """
    
    from glass.pyt import execmd
    
    rcmd = execmd(
        "v.db.join map={} column={} other_table={} other_column={}".format(
            inShp, shpCol, jnTable, joinCol
            )
        )


def join_attr_by_distance(mainTable, joinTable, workGrass, epsg_code,
                          output):
    """
    Find nearest feature and join attributes of the nearest feature
    to the mainTable
    
    Uses GRASS GIS to find near lines.
    """
    
    import os
    from glass.geo.gt.wenv.grs import run_grass
    from glass.geo.gt.fmshp    import shp_to_obj
    from glass.geo.gm.to        import df_to_geodf
    from glass.geo.gt.toshp    import df_to_shp
    from glass.pyt.oss     import fprop
    
    # Create GRASS GIS Location
    grassBase = run_grass(workGrass, location='join_loc', srs=epsg_code)
    
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grassBase, workGrass, 'join_loc', 'PERMANENT')
    
    # Import some GRASS GIS tools
    from glass.geo.gt.prox      import grs_near as near
    from glass.geo.gt.tbl.attr  import geomattr_to_db
    from glass.geo.gt.toshp.cff import shp_to_grs, grs_to_shp
    
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
    
    import os;               import pandas;
    from geopandas           import GeoDataFrame
    from glass.geo.gt.fmshp       import shp_to_obj
    from glass.geo.gt.toshp       import df_to_shp
    from glass.geo.gt.toshp.coord import shpext_to_boundshp
    from glass.geo.gt.torst       import shp_to_rst
    from glass.geo.gm.to           import df_to_geodf
    from glass.geo.gt.wenv.grs    import run_grass
    from glass.pyt.df.joins   import join_dfs
    from glass.pyt.df.agg     import df_groupBy
    from glass.pyt.oss        import fprop, mkdir
    
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
    
    import grass.script       as grass
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, workspace, "grs_loc", "PERMANENT")
    
    from glass.geo.gt.nop.local import combine
    from glass.geo.gt.prop.rst  import get_rst_report_data
    from glass.geo.gt.toshp.cff import shp_to_grs, grs_to_shp
    from glass.geo.gt.torst     import shp_to_rst
    
    # Add data to GRASS GIS
    mainVector = shp_to_grs(
        mainLines, fprop(mainLines, 'fn', forceLower=True))
    joinVector = shp_to_grs(
        joinLines, fprop(joinLines, 'fn', forceLower=True))
    
    mainRst = shp_to_rst(
        mainVector, mainId, None, None, "rst_" + mainVector, api='pygrass'
    ); joinRst = shp_to_rst(
        joinVector, joinCol, None, None, "rst_" + joinVector, api='pygrass'
    )
    
    combRst = combine(mainRst, joinRst, "combine_rst", api="pygrass")
    
    combine_data = get_rst_report_data(combRst, UNITS="c")
    
    combDf = pandas.DataFrame(combine_data, columns=[
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
    from glass.fm          import tbl_to_obj
    from glass.pyt.xls.fld import col_name
    
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
    
    # Modules
    import os;   import pandas
    from glass.fm import tbl_to_obj
    from glass.to import obj_to_tbl
    
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
    
    from glass.fm           import tbl_to_obj
    from glass.to           import obj_to_tbl
    from glass.pyt.df.joins import sum_field_of_two_tables
    
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
    
    import os; from glass.pyt.oss import lst_ff, fprop
    
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

