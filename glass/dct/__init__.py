"""
Tables to Pandas Dataframe
"""

def tbl_to_obj(tblFile, sheet=None, useFirstColAsIndex=None,
              _delimiter=None, encoding_='utf8', output='df',
              fields=None, colsAsArray=None):
    """
    Table File to Pandas DataFrame
    
    output Options:
    - df;
    - dict;
    - array;
    """
    
    from glass.pys.oss import fprop
    
    fFormat = fprop(tblFile, 'ff')
    
    if fFormat == '.dbf':
        """
        Convert dBase to Pandas Dataframe
        """
        
        from simpledbf import Dbf5
        
        dbfObj = Dbf5(tblFile)
        
        tableDf = dbfObj.to_dataframe()
    
    elif fFormat == '.ods':
        """
        ODS file to Pandas Dataframe
        """
        
        import json
        import pandas
        from pyexcel_ods import get_data
        
        if not sheet:
            raise ValueError("You must specify sheet name when converting ods files")
        data = get_data(tblFile)[sheet]
        
        tableDf = pandas.DataFrame(data[1:], columns=data[0])
    
    elif fFormat == '.xls' or fFormat == '.xlsx':
        """
        XLS to Pandas Dataframe
        """
        
        import pandas
        from glass.pys  import obj_to_lst
        
        sheet = 0 if not sheet else sheet
        
        indexCol = 0 if useFirstColAsIndex else None
        
        tableDf = pandas.read_excel(
            tblFile, sheet, index_col=indexCol,
            encoding='utf-8', dtype='object',
            usecols=obj_to_lst(fields) if fields != "ALL" else None
        )
    
    elif fFormat == '.txt' or fFormat == '.csv':
        """
        Text file to Pandas Dataframe
        """
        
        import pandas
        
        if not _delimiter:
            raise ValueError(
                "You must specify _delimiter when converting txt files"
            )
        
        tableDf = pandas.read_csv(
            tblFile, sep=_delimiter, low_memory=False,
            encoding=encoding_
        )
    
    else:
        raise ValueError('{} is not a valid table format!'.format(fFormat))
    
    if fields:
        from glass.pys  import obj_to_lst
        
        fields = obj_to_lst(fields)
        if fields:
            delCols = []
            for fld in list(tableDf.columns.values):
                if fld not in fields:
                    delCols.append(fld)
            
            if delCols:
                tableDf.drop(delCols, axis=1, inplace=True)
    
    if output != 'df':
        if output == 'dict':
            orientation = "index" if not colsAsArray else "list"
        
        elif output == 'array':
            tableDf["FID"] = tableDf.index
            
            orientation = "records"
        
        tableDf = tableDf.to_dict(orient=orientation)
    
    return tableDf


"""
Python data to File Data
"""

def obj_to_tbl(pyObj, outTbl, delimiter=None, wIndex=None,
               sheetsName=None, sanitizeUtf8=True):
    """
    Python object to data File
    """
    
    def sanitizeP(row, cols):
        for c in cols:
            try:
                _c = int(row[c])
            except:
                try:
                    row[c] = str(row[c])
                except:
                    pass
        
        return row
    
    import pandas
    from glass.pys.oss import fprop
    
    ff = fprop(outTbl, 'ff')
    
    if ff == '.txt' or ff == '.csv' or ff == '.tsv':
        if not delimiter:
            raise ValueError((
                "To save your data into a text file, you need to give a value "
                "to the delimiter input parameter"
            ))
        
        if type(pyObj) == pandas.DataFrame:
            pyObj.to_csv(outTbl, sep=delimiter, encoding='utf-8', index=wIndex)
        
        else:
            raise ValueError((
                "pyObj has an invalid data type"
            ))
    
    elif ff == '.xlsx' or ff == '.xls':
        from glass.pys      import obj_to_lst
        from glass.pys.oss import fprop
        
        dfs = [pyObj] if type(pyObj) != list else pyObj
        sheetsName = obj_to_lst(sheetsName)
        
        for df in dfs:
            if type(df) != pandas.DataFrame:
                raise ValueError("pyObj has an invalid data type")
            
        if sanitizeUtf8:
            for i in range(len(dfs)):
                COLS = list(dfs[i].columns.values)
                
                dt = dfs[i].apply(lambda x: sanitizeP(x, COLS), axis=1)
                
                dfs[i] = dt
            
        writer = pandas.ExcelWriter(outTbl, engine='xlsxwriter')
        
        for i in range(len(dfs)):
            dfs[i].to_excel(
                writer,
                sheet_name="{}_{}".format(
                    fprop(outTbl, 'fn'), str(i)
                ) if not sheetsName or i+1 > len(sheetsName) else sheetsName[i],
                index=wIndex
            )
        
        writer.save()
    
    elif ff == '.dbf':
        import numpy as np
        import pandas
        import pysal
        
        type2spec = {int: ('N', 20, 0),
            np.int64: ('N', 20, 0),
            float: ('N', 36, 15),
            np.float64: ('N', 36, 15),
            str: ('C', 14, 0)
        }
        
        types = [type(pyObj[i].iloc[0]) for i in pyObj.columns]
        specs = [type2spec[t] for t in types]
        
        with pysal.open(outTbl, 'w') as db:
            db.header = list(df.columns)
            db.field_spec = specs
            for i, row in df.T.iteritems():
                db.write(row)
    
    else:
        raise ValueError('{} is not a valid table format!'.format(ff))
    
    return outTbl


def tbl_to_tbl(inTbl, outTbl, inSheet=None, txtDelimiter=None,
               inTxtDelimiter=None, inEncoding='utf-8'):
    """
    Convert data format
    """
    
    from glass.dct import tbl_to_obj
    
    data = tbl_to_obj(
        inTbl, sheet=inSheet,
        encoding_=inEncoding, _delimiter=inTxtDelimiter
    )
    
    outTbl = obj_to_tbl(data, outTbl, delimiter=txtDelimiter)
    
    return outTbl


def db_to_tbl(db, tables, outTbl, txtDelimiter=None, dbAPI='psql',
              outTblF=None, sheetsNames=None):
    """
    Database data to File table
    
    API's Avaialble:
    * psql;
    * sqlite;
    * mysql;
    """
    
    import os
    from glass.pys         import obj_to_lst
    from glass.dct.sql.fm import q_to_obj
    
    if tables == 'ALL':
        from glass.sql.prop import lst_tbl
        
        tables = lst_tbl(db, schema='public', excludeViews=True, api=dbAPI)
    else:
        tables = obj_to_lst(tables)
    
    sheetsNames = obj_to_lst(sheetsNames)
    
    outTblF = None if not outTblF else outTblF \
        if outTblF[0] == '.' else '.' + outTblF
    
    if len(tables) > 1:
        if not sheetsNames:
            if not os.path.isdir(outTbl) or not outTblF:
                raise ValueError((
                    "When tables has more than one table, "
                    "outTbl must be dir and outTblF must be specified"
                ))
    
    elif len(tables) == 1:
        if os.path.isdir(outTbl) and outTblF:
            outTbl = os.path.join(outTbl, tables[0] + outTblF)
        
        elif os.path.isdir(outTbl) and not outTbl:
            raise ValueError((
                'We find only a table to export and outTbl is a dir. '
                'Please give a path to a file or specify the table format '
                'using outTblF format'
            ))
        
        else:
            outTbl = outTbl
    
    else:
        raise ValueError(
            "tables value is not valid"
        )   
    
    DFS = [q_to_obj(db, t if t.startswith(
        "SELECT") else "SELECT * FROM {}".format(t), db_api=dbAPI
    ) for t in tables]
    
    if os.path.splitext(outTbl)[1] != '':
        from glass.pys.oss import fprop
        
        ff = fprop(outTbl, 'ff')
        
        if ff == '.xlsx' or ff == '.xls':
            obj_to_tbl(DFS, outTbl, sheetsName=sheetsNames, sanitizeUtf8=None)
            
            return outTbl
    
    for i in range(len(DFS)):
        obj_to_tbl(
            DFS[i],
            outTbl if len(DFS) == 1 else os.path.join(
                outTbl, tables[i] + outTblF
            ),
            delimiter=txtDelimiter,
            sheetsName=sheetsNames
        )
    
    return outTbl


"""
To XLS
"""

def dict_to_xls(dataDict, xlsout_path, outSheet):
    """
    Python Dict to a XLS File

    dict = {
        row_1 : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        },
        row_2 : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        },
        ...,
        row_n : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        }
    }
          | col_1 | col_2 | ... | col_n
    row_1 | XXXXX | XXXXX | ... | XXXXX
    row_2 | XXXXX | XXXXX | ... | XXXXX
      ... | XXXXX | XXXXX | ... | XXXXX
    row_n | XXXXX | XXXXX | ... | XXXXX
    """

    import xlwt

    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(outSheet)

    # Write Columns Titles
    new_sheet.write(0, 0, 'ID')
    l = 0
    COLUMNS_ORDER = []

    for fid in dataDict:
        if not l:
            c = 1
            for col in dataDict[fid]:
                COLUMNS_ORDER.append(col)
                new_sheet.write(l, c, col)
                c+=1
            l += 1
        else:
            break

    # Write data - Columns are written by the same order
    for fid in dataDict:
        new_sheet.write(l, 0, fid)

        c = 1
        for col in COLUMNS_ORDER:
            new_sheet.write(l, c, dataDict[fid][col])
            c+=1
        l+=1

    # Save result
    out_xls.save(xlsout_path)
    
    return xlsout_path

