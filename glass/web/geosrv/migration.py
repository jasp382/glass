"""
Import data to Geoserver
"""


def pgtables_to_layer_withStyle_by_col(
    pgtables, sldData, db, workName=None, storeName=None, sldGeom='Polygon',
    DATATYPE='QUANTITATIVE', TABLE_DESIGNATION=None,
    COL_DESIGNATION=None, exclude_cols=None, pathToSLDfiles=None):
    """
    Create a new Geoserver Workspace, create a postgis store and one layer
    for each table in 'pgtables'. Each layer will have
    multiple styles - one style by column in it.
    
    Parameters:
    1) pgtables
    - List of PSQL tables to be transformed as Geoserver Layers
    
    2) sldData
    - sldData should be a xls table with the styles specifications.
    For QUANTITATIVE DATA: The table should have two sheets: one for
    colors and other for intervals:
    
    COLORS SHEET STRUCTURE (Sheet Index = 0):
    cls_id | R | G | B | STROKE_R | STROKE_G | STROKE_B | STROKE_W
       1   | X | X | X |    X     |    X     |    X     |    1
       2   | X | X | X |    X     |    X     |    X     |    1
       3   | X | X | X |    X     |    X     |    X     |    1
       4   | X | X | X |    X     |    X     |    X     |    1
       5   | X | X | X |    X     |    X     |    X     |    1
    
    INTERVALS SHEET STRUCTURE (Sheet Index = 1):
          | 0 | 1 |  2 |  3 |  4 |  5
    col_0 | 0 | 5 | 10 | 15 | 20 | 25
    col_1 | 0 | 6 | 12 | 18 | 24 | 30
    ...
    col_n | 0 | 5 | 10 | 15 | 20 | 25
    
    For CATEGORICAL DATA: The table should have only one sheet:
    CATEGORICAL SHEET STRUCTURE
           | R | G | B | STROKE_R | STROKE_G | STROKE_B | STROKE_W
    attr_1 | X | X | X |    X     |    X     |    X     |    1
    attr_2 | X | X | X |    X     |    X     |    X     |    1
    ...
    attr_n | X | X | X |    X     |    X     |    X     |    1
    
    3) pgsql_con
    - Dict with parameters that will be used to connect to PostgreSQL
    d = {
        'HOST' : 'localhost', 'PORT' : '5432', 'USER' : 'postgres',
        'PASSWORD' : 'admin', 'DATABASE' : 'db_name'
    }
    
    4) workName
    - String with the name of the Geoserver workspace that will be created
    
    5) storeName
    - String with the name of the Geoserver store that will be created
    
    6) geoserver_con
    - Dict with parameters to connect to Geoserver
    
    7) sldGeom
    - Data Geometry. At the moment, the options 'Polygon' and 'Line' are
    valid.
    
    8) DATATYPE='QUANTITATIVE' | 'CATEGORICAL'
    
    9) TABLE_DESIGNATION
    - Table with the association between pgtables name and the designation
    to be used to name the Geoserver Layer.
    
    10) COL_DESIGNATION 
    - Table xls with association between each column and one
    style that will be used to present the information of that column.
    The style designation could not have blank characters.
    
    11) exclude_cols
    - One style will be created for each column in one pgtable. The columns
    in 'exclude_cols' will not have a style.
    
    12) pathToSLDfiles
    - Absolute path to the folder where the SLD (Style Layer Descriptor)
    will be stored.
    """
    
    import os; from glass.pyt    import obj_to_lst
    from glass.fm                import tbl_to_obj
    from glass.pyt.oss           import mkdir
    from glass.sql.i             import cols_name
    from glass.web.geosrv.ws     import create_ws
    from glass.web.geosrv.stores import create_pgstore
    from glass.web.geosrv.lyrs   import pub_pglyr
    from glass.web.geosrv.sty    import create_style
    from glass.web.geosrv.sty    import lst_styles
    from glass.web.geosrv.sty    import del_style
    from glass.web.geosrv.sty    import assign_style_to_layer
    from glass.web.geosrv.sld    import write_sld
    
    # Sanitize PGtables
    pgtables = obj_to_lst(pgtables)
    
    if not pgtables:
        raise ValueError('pgtables value is not valid!')
    
    exclude_cols = obj_to_lst(exclude_cols)
    
    STY_DESIGNATION = tbl_to_obj(
        COL_DESIGNATION, useFirstColAsIndex=True, output='dict', 
        colsAsArray=True
    ) if COL_DESIGNATION else None
    
    LYR_DESIGNATION = tbl_to_obj(
        TABLE_DESIGNATION, useFirstColAsIndex=True, output='dict',
        colsAsArray=True
    ) if TABLE_DESIGNATION else None
    
    # Get intervals and colors data
    if DATATYPE == 'QUANTITATIVE':
        if os.path.exists(sldData):
            FF = os.path.splitext(sldData)[1]
            if FF == '.xls' or FF == '.xlsx':
                colorsDict    = tbl_to_obj(
                    sldData, sheet=0, useFirstColAsIndex=True, output='dict'
                ); intervalsDict = tbl_to_obj(
                    sldData, sheet=1, useFirstColAsIndex=True, output='dict'
                )
            
            else:
                raise ValueError((
                    'At the moment, for DATATYPE QUANTITATIVE, sldData '
                    'has to be a xls table'
                ))
        
        else:
            raise ValueError((
                '{} is not a valid file'
            ).format(sldData))
    
    elif DATATYPE == 'CATEGORICAL':
        if os.path.exists(sldData):
            if os.path.splitext(sldData)[1] == 'xls':
                colorsDict = tbl_to_obj(
                    sldData, sheet=0, useFirstColAsIndex=True, output='dict'
                )
            
            else:
                raise ValueError((
                    'At the moment, for DATATYPE CATEGORICAL, sldData '
                    'has to be a xls table'
                ))
        else:
            raise ValueError((
                '{} is not a valid file'
            ).format(sldData))
    
    else:
        raise ValueError('{} is not avaiable at the moment'.format(DATATYPE))
    
    # Create Workspace
    workName = 'w_{}'.format(db) if not workName else workName
    
    create_ws(workName, overwrite=True)
    
    # Create Store
    storeName = db if not storeName else storeName
    create_pgstore(storeName, workName, db)
    
    # Create folder for sld's
    wTmp = mkdir(os.path.join(
        os.path.dirname(sldData), 'sldFiles'
    )) if not pathToSLDfiles else pathToSLDfiles
    
    # List styles in geoserver
    STYLES = lst_styles()
    
    # For each table in PGTABLES
    for PGTABLE in pgtables:
        # Publish Postgis table
        TITLE = None if not LYR_DESIGNATION else LYR_DESIGNATION[PGTABLE][0]
        pub_pglyr(workName, storeName, PGTABLE, title=TITLE)
        
        # List PGTABLE columns
        pgCols = cols_name(db, PGTABLE)
        
        # For each column
        for col in pgCols:
            if exclude_cols and col in exclude_cols:
                continue
            
            STYLE_NAME = '{}_{}'.format(
                PGTABLE, STY_DESIGNATION[col][0]
            ) if STY_DESIGNATION else '{}_{}'.format(PGTABLE, col)
            
            if STYLE_NAME in STYLES:
                del_style(STYLE_NAME)
            
            # Create Object with association between colors and intervals
            d = {}
            OPACITY = str(colorsDict[1]['OPACITY'])
            for i in colorsDict:
                d[i] = {
                    'R'   : colorsDict[i]['R'],
                    'G'   : colorsDict[i]['G'],
                    'B'   : colorsDict[i]['B']
                }
                
                if DATATYPE == 'QUANTITATIVE':
                    d[i]['min'] = intervalsDict[col][i-1]
                    d[i]['max'] = intervalsDict[col][i]
                
                if 'STROKE_R' in colorsDict[i] and \
                   'STROKE_G' in colorsDict[i] and \
                   'STROKE_B' in colorsDict[i]:
                    d[i]['STROKE'] = {
                        'R' : colorsDict[i]['STROKE_R'],
                        'G' : colorsDict[i]['STROKE_G'],
                        'B' : colorsDict[i]['STROKE_B']
                    }
                    
                    if 'STROKE_W' in colorsDict[i]:
                        d[i]['STROKE']['WIDTH'] = colorsDict[i]['STROKE_W']
            
            # Create SLD
            sldFile = write_sld(
                col, d,
                os.path.join(wTmp, '{}.sld'.format(col)),
                geometry=sldGeom, DATA=DATATYPE,
                opacity=OPACITY
            )
            
            # Create Style
            create_style(STYLE_NAME, sldFile)
            
            # Apply SLD
            assign_style_to_layer(STYLE_NAME, PGTABLE)


def pgtables_groups_to_layers(groups_of_tables, db, workName, storeName):
    """
    Import all tables in pgsql database to geoserver
    
    Each table belongs to a group. One group has the same basename. One group
    is related to a single style specified in groups_of_tables
    
    groups_of_tables = {
        group_basename : path_to_sld_file,
        ...
    }
    """
    
    import os; from glass.sql.i  import lst_tbl
    from glass.web.geosrv.ws     import create_ws
    from glass.web.geosrv.stores import create_pgstore
    from glass.web.geosrv.lyrs   import pub_pglyr
    from glass.web.geosrv.sty    import create_style
    from glass.web.geosrv.sty    import lst_styles
    from glass.web.geosrv.sty    import del_style
    from glass.web.geosrv.sty    import assign_style_to_layer
    
    # Create a new workspace
    workName = 'w_{}'.format(db) if not workName else workName
    
    create_ws(workName, overwrite=True)
    
    # Create a new store
    storeName = db if not storeName else storeName
    create_pgstore(storeName, workName, db)
    
    # List styles
    STYLES = lst_styles()
    
    # For each group:
    for group in groups_of_tables:
        print("START PROCESSING {} GROUP".format(group))
        
        # - Identify tables
        tables = lst_tbl(db, basename=group, excludeViews=True)
        
        # - Create Style
        STYLE_NAME = os.path.splitext(os.path.basename(groups_of_tables[group]))[0]
        if STYLE_NAME in STYLES:
            del_style(STYLE_NAME)
        
        create_style(STYLE_NAME, groups_of_tables[group])
        
        # - Create layers
        # - Assign style
        for table in tables:
            TITLE = 'lyr_{}'.format(table)
            pub_pglyr(workName, storeName, table, title=TITLE)
            
            assign_style_to_layer(STYLE_NAME, table)
        
        print("{} GROUP IS IN GEOSERVER".format(group))

