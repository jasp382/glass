"""
Django database management
"""

def get_next_pk(modelcls, pkcol=None):
    """
    Return next primary key of one model
    """

    from django.db import connection

    pkcol = 'id' if not pkcol else pkcol

    c = connection.cursor()

    tname = modelcls._meta.db_table

    c.execute(f"SELECT nextval('{tname}_{pkcol}_seq')")
    
    row = c.fetchone()

    return row[0]
