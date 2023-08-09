"""
Dump Databases and their tables
"""

from glass.pys import execmd
from glass.cons.psql import con_psql


def dump_db(db, outSQL, api='psql'):
    """
    DB to SQL Script
    """
    
    if api == 'psql':
        

        condb = con_psql()

        cmd = (
            f"pg_dump -U {condb['USER']} -h {condb['HOST']} "
            f"-p {condb['PORT']} -w {db} > {outSQL}"
        )
    
    elif api == 'mysql':
        from glass.cons.mysql import con_mysql

        condb = con_mysql()

        cmd = (
            f"mysqldump -u {condb['USER']} --port {condb['PORT']} "
            f"-p{condb['PASSWORD']} --host {condb['HOST']} "
            f"{db} > {outSQL}"
        )
    
    else:
        raise ValueError(f'{api} API is not available')
    
    outcmd = execmd(cmd)
    
    return outSQL


def dump_tbls(db, tables, outsql, startWith=None):
    """
    Dump one table into a SQL File
    """
    
    from glass.pys import obj_to_lst
    
    tbls = obj_to_lst(tables)
    
    if startWith:
        from glass.prop.sql import lst_tbl
        
        db_tbls = lst_tbl(db, api='psql')
        
        dtbls = []
        for t in db_tbls:
            for b in tbls:
                if t.startswith(b):
                    dtbls.append(t)
        
        tbls = dtbls
    
    condb = con_psql()

    user, host, port = condb["USER"], host=condb["HOST"], condb["PORT"]
    tbl = " ".join([f"-t {t}" for t in tbls])
    
    outcmd = execmd((
        f"pg_dump -Fc -U {user} -h {host} -p {port} "
        f"-w {tbl} {db} > {outsql}"
    ))
    
    return outsql

