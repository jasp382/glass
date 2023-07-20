"""
Summarize tables
"""

def summarize_table_fields(table, outFld, fld_name_fld_name=None):
    """
    Summarize all fields in a table
    """
    
    import os
    from glass.pys      import execmd
    from glass.pys.oss  import mkdir
    from glass.prop.col import lst_cols
    
    # List table fields:
    fields = lst_cols(table)

    # Get table name
    tbl = os.path.splitext(os.path.basename(table))[0]
    
    # For each field, query data to summarize the values in the field
    cmd = 'ogr2ogr {o} {i} -dialect sqlite -sql "{s};"'
    
    if not os.path.exists(outFld):
        mkdir(outFld)
    
    for field in fields:
        outTbl = os.path.join(outFld, f'{field}.dbf')

        f_ = '' if not fld_name_fld_name else f'{fld_name_fld_name}, '

        sql = f'SELECT {f_}{field} FROM {tbl} GROUP BY {field}'
        
        outcmd = execmd(cmd.format(i=table, o=outTbl, s=sql))

