"""
Python data to File Data
"""

import pandas as pd
import geopandas as gp

from glass.pys.oss import fprop


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
        from glass.pys import obj_to_lst
        
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
                sheet_name=f"{fprop(outTbl, 'fn')}_{str(i)}"[:30] \
                    if not sheetsName or i+1 > len(sheetsName) else sheetsName[i],
                index=wIndex
            )
        
        writer.close()
    
    elif ff == '.dbf':
        import numpy as np
        import pysal
        import dbf

        type2spec = {
            int        : ('N', 20, 0),
            np.int32   : ('N', 20, 0),
            np.int64   : ('N', 20, 0),
            float      : ('N', 36, 15),
            np.float32 : ('N', 36, 15),
            np.float64 : ('N', 36, 15),
            str        : ('C', 14, 0)
        }

        cols = pyObj.columns.values

        types = [type(pyObj[i].iloc[0]) for i in pyObj.columns]

        specs = [type2spec[t] for t in types]
        specs_str = "; ".join([
            f"{cols[i]} {specs[i][0]}({specs[i][1]},{specs[i][2]})" \
                for i in range(len(cols))
        ])

        ntbl = dbf.Table(
            filename=outTbl,
            field_specs=specs_str,
            on_disk=True
        )

        with ntbl:
            for row in pyObj.itertuples(index=False):
                ntbl.append(tuple(row))
    
    else:
        raise ValueError(f'{ff} is not a valid table format!')
    
    return outTbl


def fext_to_geof(inF, outF, ocellsize=10, epsg=None, oepsg=None):
    """
    Extent of a File to Raster or Shapefile
    """
    
    from glass.dtt.toshp import coords_to_boundshp
    from glass.dtt.rst.torst import ext_to_rst
    from glass.prop.ext  import get_ext
    from glass.prop.df   import is_shp, is_rst
    from glass.prop.prj  import get_epsg
    
    # Get extent
    left, right, bottom, top = get_ext(inF)
    
    # Get EPSG of inF
    epsg = get_epsg(inF) if not epsg else epsg
    
    # Export Boundary
    isrst, isshp = is_rst(outF), is_shp(outF)
    
    if isrst and not isshp:
        of = ext_to_rst(
            (left, top), (right, bottom), outF,
            cellsize=ocellsize, epsg=epsg, outEpsg=oepsg,
            invalidResultAsNull=None
        )
    elif not isrst and isshp:
        of = coords_to_boundshp(
            (left, top), (right, bottom),
            epsg, outF, outEpsg=oepsg
        )
        
    else:
        raise ValueError(f'{inF} is not recognized as a file with GeoData')
    
    return of

