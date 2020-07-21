"""
Select using references in other supports
"""


def select_using_excel_refs(db_name, excel_file, sheet_name,
                            pgtable, ref_fields,
                            tableInRef, tableOutRef=None):
    """
    Split PGTABLE using references in excel table
    
    Create two tables:
    * One with similar rows - columns combination are in excel table;
    * One with rows not in excel table.
    
    TODO: Check if it's works. 
    """
    
    from glass.dct.fm import tbl_to_obj
    from glass.sql.i  import cols_type
    from glass.dct.to.sql import q_to_ntbl
    
    def to_and(row, cols, ctype):
        def get_equal(_type):
            return '{}=\'{}\'' if _type == str else '{}={}'
        
        row['AND_E'] = ' AND '.join(
            get_equal(ctype[col]).format(col, row[col]) for col in cols
        )
        
        row['AND_E'] = '(' + row['AND_E'] + ')'
        
        return row
    
    # Get excel data
    table = tbl_to_obj(excel_file, sheet=sheet_name)
    
    # Get reference fields type
    TYPE_COLS = cols_type(db_name, pgtable)
    
    table = table.apply(lambda x: to_and(x, ref_fields, TYPE_COLS))
    
    whr_equal = ' OR '.join(table['AND_E'])
    
    q_to_ntbl(db_name, tableInRef, "SELECT * FROM {} WHERE {}".format(
        pgtable, whr_equal
    ), api='psql')
    
    if tableOutRef:
        COLS_RELATION = " AND ".join(["{ft}.{f} = {st}.{f}".format(
            ft=pgtable, f=col, st=tableInRef
        ) for col in TYPE_COLS])
    
        q_to_ntbl(db_name, tableOutRef, (
            "SELECT {ft}.* FROM {ft} LEFT JOIN {st} ON "
            "{rel} WHERE {st}.{c} IS NULL"
        ).format(
            ft=pgtable, st=tableInRef, rel=COLS_RELATION,
            c=TYPE_COLS.keys()[0]
        ), api='psql')

