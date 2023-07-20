"""
Table Statistics
"""

def tbl_to_areamtx(inShp, col_a, col_b, outXls, db=None, with_metrics=None):
    """
    Table to Matrix
    
    Table as:
        FID | col_a | col_b | geom
    0 |  1  |   A   |   A   | ....
    0 |  2  |   A   |   B   | ....
    0 |  3  |   A   |   A   | ....
    0 |  4  |   A   |   C   | ....
    0 |  5  |   A   |   B   | ....
    0 |  6  |   B   |   A   | ....
    0 |  7  |   B   |   A   | ....
    0 |  8  |   B   |   B   | ....
    0 |  9  |   B   |   B   | ....
    0 | 10  |   C   |   A   | ....
    0 | 11  |   C   |   B   | ....
    0 | 11  |   C   |   D   | ....
    
    To:
    classe | A | B | C | D
       A   |   |   |   | 
       B   |   |   |   |
       C   |   |   |   |
       D   |   |   |   |
    
    col_a = rows
    col_b = cols

    api options:
    * pandas;
    * psql;
    """

    # TODO: check if col_a and col_b exists in table

    if not db:
        import pandas as pd
        import numpy as np
        from glass.rd.shp import shp_to_obj
        from glass.wt    import obj_to_tbl
    
        # Open data
        df = shp_to_obj(inShp)

        # Remove nan values
        df = df[pd.notnull(df[col_a])]
        df = df[pd.notnull(df[col_b])]
    
        # Get Area
        df['realarea'] = df.geometry.area / 1000000
    
        # Get rows and Cols
        rows = df[col_a].unique()
        cols = df[col_b].unique()
        refval = list(np.sort(np.unique(np.append(rows, cols))))
    
        # Produce matrix
        outDf = []
        for row in refval:
            newCols = [row]
            for col in refval:
                newDf = df[(df[col_a] == row) & (df[col_b] == col)]

                if not newDf.shape[0]:
                    newCols.append(0)
                
                else:
                    area = newDf.realarea.sum()
            
                    newCols.append(area)
        
            outDf.append(newCols)
    
        outcols = ['class'] + refval
        outDf = pd.DataFrame(outDf, columns=outcols)

        if with_metrics:
            from glass.cls.eval import get_measures_for_mtx

            out_df = get_measures_for_mtx(outDf, 'class')

            return obj_to_tbl(out_df, outXls)
    
        # Export to Excel
        return obj_to_tbl(outDf, outXls)
    
    else:
        from glass.pys.oss        import fprop
        from glass.sql.db      import create_db
        from glass.prop.sql    import db_exists
        from glass.it.db       import shp_to_psql
        from glass.dtt.tomtx.sql import tbl_to_area_mtx
        from glass.it          import db_to_tbl

        # Create database if not exists
        is_db = db_exists(db)

        if not is_db:
            create_db(db, api='psql')

        # Add data to database
        tbl = shp_to_psql(db, inShp, api='shp2pgsql')

        # Create matrix
        mtx = tbl_to_area_mtx(db, tbl, col_a, col_b, fprop(outXls, 'fn'))

        # Export result
        return db_to_tbl(db, mtx, outXls, sheetsNames='matrix')

