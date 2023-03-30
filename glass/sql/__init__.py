"""
Tools for DBMS and SQL
"""


def psql_cmd(db_name, sqlfile, dbcon=None):
    """
    Run a sql file do whatever is on that script
    """
    
    import os
    from glass.pys        import execmd
    from glass.cons.psql import con_psql

    cdb = con_psql(db_set=dbcon)

    if os.path.isdir(sqlfile):
        from glass.pys.oss import lst_ff

        sqls = lst_ff(sqlfile, file_format='.sql')
    else:
        sqls = [sqlfile]
    
    cmd = (
        f"psql -h {cdb['HOST']} -U {cdb['USER']} "
        f"-p {cdb['PORT']} -w {db_name} < "
    )
    
    for s in sqls:
        outcmd = execmd(f"{cmd}{s}")
    
    return db_name

