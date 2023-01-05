"""
Do Something with features
"""


def multipart_to_shp(shp, oshp):
    """
    ID multipart features in a Feature Class
    and export them to a new feature class
    """

    from glass.rd.shp import shp_to_obj
    from glass.wt.shp import df_to_shp

    df = shp_to_obj(shp)

    df["geomtype"] = df.geometry.geom_type

    df = df[df.geomtype == 'MultiLineString']

    df_to_shp(df, oshp)

    return oshp

