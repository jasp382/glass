"""
Tables to Tables
"""


def tbl_to_tbl(intbl, out, inSheet=None, txtDelimiter=None,
               inTxtDelimiter=None, inEncoding='utf-8'):
    """
    Convert data format
    """

    from glass.pys.oss import fprop
    from glass.rd import tbl_to_obj
    from glass.wt import obj_to_tbl

    it_f = fprop(intbl, 'ff')
    ot_f = fprop(out, 'ff')

    _i = 1 if it_f == '.dbf' or it_f == '.xlsx' else 0
    _o = 1 if ot_f == '.dbf' or ot_f == '.xlsx' else 0

    if _i and _o:
        from glass.pys     import execmd
        from glass.prop.df import drv_name

        ocmd = execmd((
            f'ogr2ogr --config OGR_XLSX_HEADERS FORCE '
            f'-f "{drv_name(out)}" {out} {intbl} '
        ))
    
    else:
        data = tbl_to_obj(
            intbl, sheet=inSheet,
            encoding_=inEncoding, _delimiter=inTxtDelimiter
        )
    
        out = obj_to_tbl(data, out, delimiter=txtDelimiter)
    
    return out


def db_to_tbl(db, tables, outTbl, txtDelimiter=None, dbAPI='psql',
              outTblF=None, sheetsNames=None, _dbset=None):
    """
    Database data to File table
    
    API's Avaialble:
    * psql;
    * sqlite;
    * mysql;
    """
    
    import os
    from glass.pys   import obj_to_lst
    from glass.sql.q import q_to_obj
    from glass.wt    import obj_to_tbl
    
    if tables == 'ALL':
        from glass.prop.sql import lst_tbl
        
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
        "SELECT") else f"SELECT * FROM {t}",
        db_api=dbAPI, dbset='default' if not _dbset else _dbset
    ) for t in tables]
    
    if os.path.splitext(outTbl)[1] != '':
        from glass.pys.oss import fprop
        
        ff = fprop(outTbl, 'ff')
        
        if ff == '.xlsx' or ff == '.xls':
            obj_to_tbl(
                DFS, outTbl,
                sheetsName=sheetsNames, sanitizeUtf8=None
            )
            
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

