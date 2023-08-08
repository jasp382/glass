"""
GeoDataFrame Properties
"""

def geom_type(df, gcol="geometry"):
    """
    Return Geometry Type of a GeoDataFrame
    """

    g = df[gcol].geom_type.unique()

    if len(g) == 1:
        return g[0]
        
    elif len(g) == 0:
        raise ValueError(
            "It was not possible to identify geometry type"
        )
        
    else:
        for i in g:
            if i.startswith('Multi'):
                return i

