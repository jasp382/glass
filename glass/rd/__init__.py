"""
Read data from File
"""

def tbl_to_obj(tblFile, sheet=None, useFirstColAsIndex=None,
              _delimiter=None, encoding_='utf8', output='df',
              fields=None, colsAsArray=None, csvheader=True):
    """
    Table File to Pandas DataFrame
    
    output Options:
    - df;
    - dict;
    - array;
    """
    
    import pandas as pd
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
        
        from pyexcel_ods import get_data
        
        if not sheet:
            raise ValueError("You must specify sheet name when converting ods files")
        
        data = get_data(tblFile)[sheet]
        
        tableDf = pd.DataFrame(data[1:], columns=data[0])
    
    elif fFormat == '.xls' or fFormat == '.xlsx':
        """
        XLS to Pandas Dataframe
        """
        
        from glass.pys import obj_to_lst
        
        sheet = 0 if not sheet else sheet
        
        indexCol = 0 if useFirstColAsIndex else None
        
        tableDf = pd.read_excel(
            tblFile, sheet, index_col=indexCol,
            dtype='object',
            usecols=obj_to_lst(fields) if fields != "ALL" else None
        )
    
    elif fFormat == '.txt' or fFormat == '.csv':
        """
        Text file to Pandas Dataframe
        """
        
        if not _delimiter:
            raise ValueError(
                "You must specify _delimiter when converting txt files"
            )
        
        if csvheader:
            tableDf = pd.read_csv(
                tblFile, sep=_delimiter, low_memory=False,
                encoding=encoding_
            )
        else:
            tableDf = pd.read_csv(
                tblFile, sep=_delimiter, low_memory=False,
                encoding=encoding_, header=None
            )
    
    else:
        raise ValueError(f'{fFormat} is not a valid table format!')
    
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

