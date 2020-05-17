"""
Summarize tables
"""

def summarize_table_fields(table, outFld, fld_name_fld_name=None,
                          __upper=False):
    """
    Summarize all fields in a table
    """
    
    import os
    from glass.pyt     import execmd
    from glass.pyt.oss import mkdir
    
    # List table fields:
    fields = lst_fld(table)
    
    # For each field, query data to summarize the values in the field
    cmd = 'ogr2ogr {o} {i} -dialect sqlite -sql "{s};"'
    
    if not os.path.exists(outFld):
        tmp = mkdir(outFld)
    
    for field in fields:
        outTbl = os.path.join(outFld, '{}.dbf'.format(field))
        
        outcmd = execmd(cmd.format(
            i=table, o=outTbl,
            s='SELECT {f_}{f} FROM {t} GROUP BY {f}'.format(
                f=field,
                t=os.path.splitext(os.path.basename(table))[0],
                f_='' if not fld_name_fld_name else '{}, '.format(
                    fld_name_fld_name
                )
            )
        ))

