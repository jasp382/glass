"""
Fields
"""


def add_fields(tbl, fields, lyrN=1, api='ogr'):
    """
    Receive a feature class and a dict with the field name and type
    and add the fields in the feature class

    API Options:
    * ogr;
    * ogrinfo;
    * pygrass;
    * grass;

    For pygrass and grass field options are:
    * VARCHAR()
    * INT
    * DOUBLE PRECISION
    * DATE
    """

    if type(fields) != dict:
        raise ValueError('Fields argument should be a dict')

    import os

    if api == 'ogr':
        from osgeo           import ogr
        from glass.prop    import drv_name
        from glass.lyr.fld import fields_to_lyr

        if os.path.exists(tbl) and os.path.isfile(tbl):
            # Open table in edition mode
            __table = ogr.GetDriverByName(drv_name(
                tbl)).Open(tbl, 1)
            
            # Get Layer
            lyr = __table.GetLayer()

            # Add fields to layer
            lyr = fields_to_lyr(lyr, fields)

            del lyr
            __table.Destroy()
        
        else:
            raise ValueError('File path does not exist')
    
    elif api == 'ogrinfo':
        from glass.pys     import execmd
        from glass.pys.oss import fprop

        tname = fprop(tbl, 'fn')

        ogrinfo = 'ogrinfo {i} -sql "{s}"'

        for fld in fields:
            sql = 'ALTER TABLE {} ADD COLUMN {} {};'.format(
                tname, fld, fields[fld]
            )

            outcmd = execmd(ogrinfo.format(i=tbl, s=sql))
    
    elif api == 'grass':
        from glass.pys import execmd

        for fld in fields:
            rcmd = execmd((
                "v.db.addcolumn map={} layer={} columns=\"{} {}\" --quiet"
            ).format(tbl, lyrN, fld, fields[fld]))
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module

        for fld in fields:
            c = Module(
                "v.db.addcolumn", map=tbl, layer=lyrN,
                columns='{} {}'.format(fld, fields[fld]),
                run_=False, quiet=True
            )

            c()
    
    else:
        raise ValueError('API {} is not available'.format(api))


def fields_to_tbls(inFolder, fields, tbl_format='.shp'):
    """
    Add fields to several tables in a folder
    """
    
    from glass.pys.oss import lst_ff
    
    tables = lst_ff(inFolder, file_format=tbl_format)
    
    for table in tables:
        add_fields(table, fields, api='ogr')


def del_cols(lyr, cols, api='grass', lyrn=1):
    """
    Remove Columns from Tables
    """

    from glass.pys import obj_to_lst

    cols = obj_to_lst(cols)

    if api == 'grass':
        from glass.pys import execmd

        rcmd = execmd((
            "v.db.dropcolumn map={} layer={} columns={} "
            "--quiet"
        ).format(
            lyr, str(lyrn), ','.join(cols)
        ))
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module

        m = Module(
            "v.db.dropcolumn", map=lyr, layer=lyrn,
            columns=cols, quiet=True, run_=True
        )
    
    else:
        raise ValueError("API {} is not available".format(api))

    return lyr


def rn_cols(inShp, columns, api="ogr2ogr"):
    """
    Rename Columns in Shp

    api options:
    * ogr2ogr;
    * grass;
    * pygrass;
    """
    
    if api == "ogr2ogr":
        import os
        from glass.pys.oss    import fprop
        from glass.pys.oss    import del_file, lst_ff
        from glass.tbl.filter import sel_by_attr
        from glass.prop.col   import lst_cols
        
        # List Columns
        cols = lst_cols(inShp)
        for c in cols:
            if c in columns:
                continue
            else:
                columns[c] = c
        
        columns["geometry"] = "geometry"

        # Get inShp Folder
        inshpfld = os.path.dirname(inShp)

        # Get inShp Filename and format
        inshpname = fprop(inShp, 'fn')

        # Temporary output
        output = os.path.join(inshpfld, inshpname + '_xtmp.shp')
        
        # Rename columns by selecting data from input
        outShp = sel_by_attr(inShp, "SELECT {} FROM {}".format(
            ", ".join(["{} AS {}".format(c, columns[c]) for c in columns]),
            inshpname
        ) , output, api_gis='ogr')
        
        # Delete Original file
        infiles = lst_ff(inshpfld, filename=inshpname)
        del_file(infiles)
        
        # Rename Output file
        oufiles = lst_ff(inshpfld, filename=inshpname + '_xtmp')
        for f in oufiles:
            os.rename(f, os.path.join(inshpfld, inshpname + fprop(f, 'ff')))
    
    elif api == 'grass':
        from glass.pys import execmd

        for col in columns:
            rcmd = execmd((
                f"v.db.renamecolumn map={inShp} layer=1 "
                f"column={col},{columns[col]}"
            ))
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module

        for col in columns:
            func = Module(
                "v.db.renamecolumn", map=inShp,
                column=f"{col},{columns[col]}",
                quiet=True, run_=False
            )
            func()
    
    else:
        raise ValueError("{} is not available".format(api))
    
    return inShp


"""
Update data in Table Field
"""


def update_cols(table, upcol, nval):
    """
    Update a feature class table with new values

    new_values = {
        new_value : where statment
        new_value : None # if no where statment
    }
    
    Where with OR condition
    new_values and ref_values are dict with fields as keys and values as 
    keys values.
    """
    
    from glass.pys import execmd
    from glass.pys.oss import fprop

    tn = fprop(table, 'fn')
    
    for v in nval:
        q = "UPDATE {} SET {}={}{}".format(
            tn, upcol, str(v) if type(v) != str else "'{}'".format(str(v)),
            "" if not nval[v] else " WHERE {}".format(
                nval[v] if type(nval[v]) != list else " OR ".join(nval[v])
            )
        )
    
        ogrinfo = 'ogrinfo {} -dialect sqlite -sql "{}"'.format(table, q)
    
        # Run command
        outcmd = execmd(ogrinfo)


def filename_to_col(tables, new_field, table_format='.dbf'):
    """
    Update a table with the filename in a new field
    """
    
    import os
    from glass.pys.oss    import lst_ff
    from glass.tbl.col import add_fields
    
    if os.path.isdir(tables):
        __tables = lst_ff(tables, file_format=table_format)
    
    else:
        __tables = [tables]
    
    for table in __tables:
        add_fields(table, {new_field: 'varchar(50)'})
        
        name_tbl = os.path.splitext(os.path.basename(table))[0]
        name_tbl = name_tbl.lower() if name_tbl.isupper() else name_tbl
        update_cols(
            table, {new_field: name_tbl}
        )


"""
Geom in Dataframes to columns
"""

def pointxy_to_cols(df, geomCol="geometry", colX="x", colY="y"):
    """
    Point x, y to cols

    TODO: check if geomtype if point or MultiPoint
    """
    
    df[colX] = df[geomCol].x.astype(float)
    df[colY] = df[geomCol].y.astype(float)
    
    return df


def geom_endpoints_to_cols(df, geomCol="geometry"):
    """
    Endpoints of Geometry in GeoDataframe to columns
    """
    
    def get_endpoints(row):
        coords = list(row[geomCol].coords)
        
        row["start_x"] = coords[0][0]
        row["start_y"] = coords[0][1]
        row["end_x"]   = coords[-1][0]
        row["end_y"]   = coords[-1][1]
        
        return row
    
    newDf = df.apply(lambda x: get_endpoints(x), axis=1)
    
    return newDf

