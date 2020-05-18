"""
For every SQL File in folder:

Restore Database, run some queries and Dump result
"""

if __name__ == '__main__':
    sql_fld = '/home/jasp/mrgis/dbs'
    outfld = '/home/jasp/mrgis/zipdb'

    QS = [
        # Create ZIP Table
        ("CREATE TABLE zip_vistoburn AS "
        "SELECT rowi, coli, array_agg(pntid) AS pntid "
        "FROM vistoburn GROUP BY rowi, coli"),
        # Delete vistoburn
        "DROP TABLE IF EXISTS vistoburn"
    ]

    import os
    from gasp.sql import psql_cmd
    from gasp.pyt.oss import lst_ff, fprop
    from gasp.sql.q import exec_write_q
    from gasp.sql.fm import dump_db
    from gasp.sql.db import create_db, drop_db

    sqls = lst_ff(sql_fld)

    for sql in sqls:
        # Restore database
        new_db = create_db(fprop(sql, 'fn'))
        psql_cmd(new_db, sql)

        # Execute queries
        exec_write_q(new_db, QS)

        # Dump Database
        dump_db(new_db, os.path.join(outfld, os.path.basename(sql)), api='psql')
    
        # Drop Database
        drop_db(new_db)
