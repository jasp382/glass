"""
Data to Django Model
"""

import os

def shp_to_djg_mdl(in_shp, app, mdl, cols_map, djg_proj):
    """
    Add Geometries to Django Model
    """
    
    from django.contrib.gis.geos       import GEOSGeometry
    from django.contrib.gis.db         import models
    from glass.pys                     import __import
    from glass.wg.djg                  import get_djgprj
    from glass.rd.shp                  import shp_to_obj
    from glass.prop.prj                import shp_epsg
    from shapely.geometry.multipolygon import MultiPolygon

    def force_multi(geom):
        if geom.geom_type == 'Polygon':
            return MultiPolygon([geom])
        else:
            return geom

    application = get_djgprj(djg_proj)
    
    mdl_cls = __import(f'{app}.models.{mdl}')
    mdl_obj = mdl_cls()
        
    in_df = shp_to_obj(in_shp)
    # Check if we need to import the SHP FID 
    if 'FID' in cols_map.values():
        in_df["FID"] = in_df.index.astype(int)
    
    epsg = int(shp_epsg(in_shp))
    if not epsg:
        raise ValueError('Is not possible to recognize EPSG code of in_shp')
        
    OGR_GEOMS = [
        'POLYGON', 'MULTIPOLYGON', 'MULTILINESTRING',
        'LINESTRING', 'POINT', 'MULTIPOINT']
        
    def updateModel(row):
        for FLD in cols_map:
            if cols_map[FLD] not in OGR_GEOMS:
                # Check if field is foreign key
                field_obj = mdl_cls._meta.get_field(FLD)
                
                if not isinstance(field_obj, models.ForeignKey):
                    setattr(mdl_obj, FLD, row[cols_map[FLD]])
                
                else:
                    # If yes, use the model instance of the related table
                    # Get model of the table related com aquela cujos dados
                    # estao a ser restaurados
                    related_name = field_obj.related_model.__name__
                    
                    related_model = __import(f'{app}.models.{related_name}')
                    
                    related_obj = related_model.objects.get(
                        pk=int(row[cols_map[FLD]])
                    )
                    
                    setattr(mdl_obj, FLD, related_obj)
            
            else:
                if cols_map[FLD] == 'MULTIPOLYGON':
                    geom = force_multi(row.geometry)
                
                else:
                    geom = row.geometry
                
                setattr(mdl_obj, FLD, GEOSGeometry(
                    geom.wkt, srid=epsg
                ))
        
        mdl_obj.save()
        
    in_df.apply(lambda x: updateModel(x), axis=1)

    return 1


def pgtbl_to_mdl(djg_proj, app, model, datadb, datatbl, geom=None, epsg=None):
    """
    Import data from one PostgreSQL Table into Django Model
    """

    from glass.sql.q             import q_to_obj
    from glass.pys               import __import
    from django.contrib.gis.geos import GEOSGeometry
    from django.contrib.gis.db   import models
    from glass.wg.djg            import get_djgprj

    # Get data
    data = q_to_obj(datadb, "SELECT * FROM {}".format(datatbl), geomCol=geom, epsg=epsg)

    cols = data.columns.values

    # Get Django Application
    application = get_djgprj(djg_proj)

    # Get Model
    mdl_cls = __import(f'{app}.models.{model}')
    mdl_obj = mdl_cls()

    def upmdl(row):
        for col in cols:
            if geom and col == geom:
                # Add geometry
                setattr(mdl_obj, col, GEOSGeometry(row[col].wkt, srid=epsg))
        
            else:
                # Check if field is foreign key
                field_obj = mdl_cls._meta.get_field(col)
            
                if not isinstance(field_obj, models.ForeignKey):
                    setattr(mdl_obj, col, row[col])
            
                else:
                    related_name = field_obj.related_model.__name__
                
                    related_model = __import('{}.models.{}'.format(
                        app, related_name
                    ))
                
                    related_obj = related_model.objects.get(
                        pk=int(row[col])
                    )
                
                    setattr(mdl_obj, col, related_obj)
        mdl_obj.save()

    data.apply(lambda x: upmdl(x), axis=1)


def txt_to_db(txt, proj_path=None, delimiter='\t', encoding_='utf-8'):
    """
    Read a txt with table data and import it to the database using
    django API.
    
    Use the filename of the text file to identify the correspondent django
    model.
    
    Proj_path is not necessary if you are running this method in Django shell
    
    IMPORTANT NOTE:
    This method will work only if all foreign key columns have the same name
    of their models.
    """
    
    import codecs
    from glass.pys          import __import
    from glass.wg.djg.mdl.i import get_special_tables
    
    def sanitize_value(v):
        _v = None if v=='None' or v =='' else v
        
        if not _v:
            return _v
        else:
            try:
                __v = float(_v)
                if __v == int(__v):
                    return int(__v)
                else:
                    return __v
            except:
                return _v
    
    if not os.path.exists(txt) and not os.path.isfile(txt):
        raise ValueError('Path given is not valid')
    
    # Open Django Project
    if proj_path:
        from glass.wg.djg import get_djgprj
        
        application = get_djgprj(proj_path)
    
    from django.contrib.gis.db import models
    
    table_name = os.path.splitext(os.path.basename(txt))[0]
    
    SPECIAL_TABLES = get_special_tables()
    
    if table_name in SPECIAL_TABLES:
        str_to_import_cls = SPECIAL_TABLES[table_name]
        
    else:
        djg_app = table_name.split('_')[0]
        
        djg_model_name = '_'.join(table_name.split('_')[1:])
        
        str_to_import_cls = f'{djg_app}.models.{djg_model_name}'
    
    djangoCls = __import(str_to_import_cls)
    
    # Map data in txt
    with codecs.open(txt, 'r', encoding=encoding_) as f:
        c = 0
        data = []
        
        for l in f:
            cols = l.replace('\r', '').strip('\n').split(delimiter)
            
            if not c:
                cols_name = ['%s' % cl for cl in cols]
                c += 1
            else:
                data.append([sanitize_value(v) for v in cols])
        
        f.close()
    
    # Import data to django class and db
    __model = djangoCls()
    for row in data:
        for c in range(len(row)):
            # Check if field is a foreign key
            field_obj = djangoCls._meta.get_field(cols_name[c])
            if not isinstance(field_obj, models.ForeignKey):
                # If not, use the value
                setattr(__model, cols_name[c], row[c])
            else:
                # If yes, use the model instance of the related table
                # Get model of the table related com aquela cujos dados 
                # estao a ser restaurados
                related_name = field_obj.related_model.__name__
                related_model = __import('{a}.models.{m}'.format(
                    a=djg_app, m=related_name
                ))
                related_obj = related_model.objects.get(pk=int(row[c]))
                setattr(__model, cols_name[c], related_obj)
        __model.save()


def txts_to_db(folder, delimiter='\t', _encoding_='utf-8', proj_path=None):
    """
    List all txt files in a folder and import their data to the 
    database using django API.
    
    The txt files name must be equal to the name of the
    correspondent table.
    
    Proj_path is not necessary if you are running this method in Django shell
    """
    
    from glass.pys.oss        import lst_ff
    from glass.wg.djg.mdl.rel import order_mdl_by_rel
    
    # Open Django Project
    if proj_path:
        from glass.wg.djg import get_djgprj
        application = get_djgprj(proj_path)
    
    # List txt files
    if not os.path.exists(folder) and not os.path.isdir(folder):
        raise ValueError('Path given is not valid!')
    
    # Get importing order
    txt_tables = [
        os.path.splitext(os.path.basename(x))[0] for x in lst_ff(
            folder, file_format='.txt'
        )
    ]
    
    orderned_table = order_mdl_by_rel(txt_tables)
    
    for table in orderned_table:
        if table in txt_tables:
            print('Importing {}'.format(table))
            txt_to_db(
                os.path.join(folder, table + '.txt'),
                delimiter=delimiter,
                encoding_=_encoding_
            )
            print(f'{table} is in the database')
        else:
            print(f'Skipping {table} - there is no file for this table')


def psql_to_djgdb(sql_dumps, db_name, djg_proj=None, mapTbl=None, userDjgAPI=None):
    """
    Import PGSQL database in a SQL Script into the database
    controlled by one Django Project
    
    To work, the name of a model instance of type foreign key should be
    equal to the name of the 'db_column' clause.
    """
    
    from glass.pys            import __import
    from glass.pys            import obj_to_lst
    from glass.sql.db         import restore_tbls 
    from glass.sql.db         import create_pgdb, drop_db
    from glass.prop.sql       import lst_tbl
    from glass.sql.q          import q_to_obj
    from glass.wg.djg.mdl.rel import order_mdl_by_rel
    from glass.wg.djg.mdl.i   import lst_mdl_proj

    # Global variables
    TABLES_TO_EXCLUDE = [
        'geography_columns', 'geometry_columns',
        'spatial_ref_sys', 'raster_columns', 'raster_columns',
        'raster_overviews', 'pointcloud_formats', 'pointcloud_columns'
    ]

    # Several SQL Files are expected
    sql_scripts = obj_to_lst(sql_dumps)

    # Create Database
    tmp_db_name = f'{db_name}_xxxtmp'
    create_pgdb(tmp_db_name)
    
    # Restore tables in SQL files
    for sql in sql_scripts:
        restore_tbls(tmp_db_name, sql)
    
    # List tables in the database
    tables = [x for x in lst_tbl(
        tmp_db_name, excludeViews=True, api='psql'
    )] if not mapTbl else mapTbl
    
    # Open Django Project
    if djg_proj:
        from glass.wg.djg import get_djgprj
        application = get_djgprj(djg_proj)
    
    # List models in project
    app_mdls = lst_mdl_proj(djg_proj, thereIsApp=True, returnClassName=True)
    
    data_tbl = {}
    for t in tables:
        if t == 'auth_user' or t == 'auth_group' or t == 'auth_user_groups':
            data_tbl[t] = t
        
        elif t.startswith('auth') or t.startswith('django'):
            continue
        
        elif t not in app_mdls or t in TABLES_TO_EXCLUDE:
            continue
        
        else:
            data_tbl["{}.models.{}".format(t.split('_')[0], app_mdls[t])] = t
    
    from django.contrib.gis.db import models
    mdl_cls = [f"{m.split('_')[0]}.models.{app_mdls[m]}" for m in app_mdls]
    orderned_table = order_mdl_by_rel(mdl_cls)

    # Add default tables of Django
    def_djg_tbl = []
    if 'auth_group' in data_tbl:
        def_djg_tbl.append('auth_group')
    
    if 'auth_user' in data_tbl:
        def_djg_tbl.append('auth_user')
    
    if 'auth_user_groups' in data_tbl:
        def_djg_tbl.append('auth_user_groups')
    
    orderned_table = def_djg_tbl + orderned_table
    
    if userDjgAPI:
        for table in orderned_table:
            # Map pgsql table data
            tableData = q_to_obj(tmp_db_name, data_tbl[table], of='dict')
        
            # Table data to Django Model
            if table == 'auth_user':
                mdl_cls = __import('django.contrib.auth.models.User')
            elif table == 'auth_group':
                mdl_cls = __import('django.contrib.auth.models.Group')
            else:
                mdl_cls = __import(table)
        
            __mdl = mdl_cls()
        
            for row in tableData:
                for col in row:
                    # Check if field is a foreign key
                    field_obj = mdl_cls._meta.get_field(col)
                
                    if not isinstance(field_obj, models.ForeignKey):
                        # If not, use the value
                    
                        # But first check if value is nan (special type of float)
                        if row[col] != row[col]:
                            row[col] = None
                        
                        setattr(__mdl, col, row[col])
                
                    else:
                        # If yes, use the model instance of the related table
                        # Get model of the table related com aquela cujos dados 
                        # estao a ser restaurados
                        related_name = field_obj.related_model.__name__
                        related_model = __import(
                            f'{table.split("_")[0]}.models.{related_name}'
                        )
                    
                        # If NULL, continue
                        if not row[col]:
                            setattr(__mdl, col, row[col])
                            continue
                    
                        related_obj = related_model.objects.get(
                            pk=int(row[col])
                        )
                    
                        setattr(__mdl, col, related_obj)
                __mdl.save()
    else:
        import pandas     as pd
        from glass.sql.q  import q_to_obj
        from glass.wt.sql import df_to_db
        
        for tbl in orderned_table:
            if tbl not in data_tbl:
                continue
            
            data = q_to_obj(tmp_db_name, f"SELECT * FROM {data_tbl[tbl]}")
            
            if tbl == 'auth_user':
                data['last_login'] = pd.to_datetime(data.last_login, utc=True)
                data['date_joined'] = pd.to_datetime(data.date_joined, utc=True)
            
            df_to_db(db_name, data, data_tbl[tbl], append=True)
    
    drop_db(tmp_db_name)

