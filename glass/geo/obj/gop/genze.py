"""
Generalization
"""

def df_dissolve(df, field):
    """
    Dissolve using GeoPandas
    """

    dissDf = df.dissolve(by=field)

    return dissDf

