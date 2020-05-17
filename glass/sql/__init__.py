"""
Tools for DBMS and SQL
"""


def psql_cmd(db_name, sqlfile, dbcon=None):
    """
    Run a sql file do whatever is on that script
    """
    
    import os
    from glass.pyt       import execmd
    from glass.cons.psql import con_psql

    cdb = con_psql(db_set=dbcon)

    if os.path.isdir(sqlfile):
        from glass.pyt.oss import lst_ff

        sqls = lst_ff(sqlfile, file_format='.sql')
    else:
        sqls = [sqlfile]
    
    cmd = 'psql -h {} -U {} -p {} -w {} < {}'
    
    for s in sqls:
        outcmd = execmd(cmd.format(
            cdb['HOST'], cdb['USER'], cdb['PORT'],
            db_name, s
        ))
    
    return db_name

