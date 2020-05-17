"""
Constants for PostgreSQL Operations
"""

PG_SPECIAL_WORDS = ['table', 'column', 'natural', 'group', 'left', 'right',
                    'order']


"""
PostgreSQL Types
"""
def map_psqltypes(oid, python=True):
    """
    Relation between the oid and typename of the pg_type table
    
    To get the type associated to the key (oid), use:
    SELECT oid, typname FROM pg_type WHERE oid=18;
    """
    
    index = 1 if not python else 0
    
    pg_types = {
        18     : [str,        'text'],
        20     : [int,        'integer'],
        21     : [int,        'integer'],
        23     : [int,        'integer'],
        25     : [str,        'text'],
        700    : [float,      'decimal'],
        701    : [float,      'decimal'],
        1043   : [str,        'text'],
        1700   : [float,       'numeric'],
        16400  : ['geometry', 'geometry'],
        18013  : ['geometry', 'geometry'],
        18823  : ['geometry', 'geometry'],
        20155  : [str,        'hstore'],
        24270  : [str,        'hstore'],
        28386  : [str,        'hstore'],
        29254  : [str,        'hstore'],
        38467  : [str,        'hstore'],
        77768  : ['geometry', 'geometry'],
        147348 : ['geometry', 'geometry'],
        157351 : ['geometry', 'geometry'],
        244228 : ['geometry', 'geometry'],
        321695 : ['geometry', 'geometry']
    }
    
    if oid not in pg_types and oid >= 100000:
        return 'geometry'
    
    elif oid not in pg_types and (oid > 20155 and oid < 38467):
        if python:
            return str
        else:
            return 'text'
    
    elif oid not in pg_types and oid < 100000:
        raise ValueError('OID {} not in pg_types'.format(str(oid)))
    
    return pg_types[oid][index]


def pnd_maps_pgtypes(type_):
    __types = {
        'int32'   : 'bigint',
        'int64'   : 'bigint',
        'float32' : 'decimal',
        'float64' : 'decimal',
        'object'  : 'text'
    }
    
    return __types[type_]

def pgtypes_from_pnddf(df):
    """
    Get PGTypes from pandas dataframe
    """
    
    dataTypes = dict(df.dtypes)
    
    return {col : pnd_maps_pgtypes(
        str(dataTypes[col])) for col in dataTypes}


def con_psql(db_set='default'):
    """
    Return Dict to Connect to PostgreSQL
    """

    import json, os

    con_param = json.load(open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'con-postgresql.json'
    ), 'r'))

    db_set = 'default' if db_set == None or \
        db_set not in con_param else db_set

    return con_param[db_set]
