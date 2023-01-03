"""
Python data to File Data
"""

import pandas as pd
import geopandas as gp


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
    
    
    from glass.pys.oss import fprop
    
    ff = fprop(outTbl, 'ff')
    
    if ff == '.txt' or ff == '.csv' or ff == '.tsv':
        if not delimiter:
            raise ValueError((
                "To save your data into a text file, you need to give a value "
                "to the delimiter input parameter"
            ))
        
        if type(pyObj) == pd.DataFrame:
            pyObj.to_csv(outTbl, sep=delimiter, encoding='utf-8', index=wIndex)
        
        else:
            raise ValueError((
                "pyObj has an invalid data type"
            ))
    
    elif ff == '.xlsx' or ff == '.xls':
        from glass.pys     import obj_to_lst
        from glass.pys.oss import fprop
        
        dfs = [pyObj] if type(pyObj) != list else pyObj
        sheetsName = obj_to_lst(sheetsName)
        
        for df in dfs:
            if type(df) != pd.DataFrame and type(df) != gp.GeoDataFrame:
                raise ValueError("pyObj has an invalid data type")
            
        if sanitizeUtf8:
            for i in range(len(dfs)):
                COLS = list(dfs[i].columns.values)
                
                dt = dfs[i].apply(lambda x: sanitizeP(x, COLS), axis=1)
                
                dfs[i] = dt
            
        writer = pd.ExcelWriter(outTbl, engine='xlsxwriter')
        
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
        import pysal
        import dbf

        dbf.Table()
        
        type2spec = {
            int        : ('N', 20, 0),
            np.int64   : ('N', 20, 0),
            float      : ('N', 36, 15),
            np.float64 : ('N', 36, 15),
            str        : ('C', 14, 0)
        }
        
        types = [type(pyObj[i].iloc[0]) for i in pyObj.columns]
        specs = [type2spec[t] for t in types]
        
        with pysal.open(outTbl, 'w') as db:
            db.header = list(pyObj.columns)
            db.field_spec = specs
            for i, row in pyObj.T.iteritems():
                db.write(row)
    
    else:
        raise ValueError(f'{ff} is not a valid table format!')
    
    return outTbl

