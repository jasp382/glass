"""
SQLITE Column Types
"""

def pnd_map_sqtypes(type_):
    __types = {
        'int32'   : 'integer',
        'int64'   : 'integer',
        'float32' : 'numeric',
        'float64' : 'numeric',
        'object'  : 'text'
    }
    
    return __types[type_]


def sqtypes_from_df(df):
    """
    Get PGTypes from pandas dataframe
    """
    
    dataTypes = dict(df.dtypes)
    
    return {col : pnd_map_sqtypes(type_)(
        str(dataTypes[col])) for col in dataTypes}