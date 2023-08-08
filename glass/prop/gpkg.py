"""
GeoPackages properties
"""


def lst_gpkg_layers(gpkg):
    """
    Return a list with all layers in a 
    GeoPackage
    """

    import fiona

    layers = fiona.listlayers(gpkg)

    return layers

