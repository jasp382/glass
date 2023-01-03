"""
Image Properties
"""

def get_nd(img):
    """
    Return NoData Value
    """

    band = img.GetRasterBand(1)

    return band.GetNoDataValue()


def get_cell_size(img):
    """Return Cellsize"""

    (tlx, x, xr, tly, yr, y) = img.GetGeoTransform()

    return x, y


def rst_epsg(img, isproj=None):
    """
    Return Raster EPSG
    """

    from osgeo import osr

    proj = osr.SpatialReference(wkt=img.GetProjection())

    if not proj:
        raise ValueError(
            'img obj has not Spatial Reference assigned!'
        )
    
    epsg = int(str(proj.GetAttrValue('AUTHORITY', 1)))

    if not isproj:
        return epsg
    
    else:
        if proj.IsProjected:
            mod_proj = proj.GetAttrValue(str('projcs'))

            if not mod_proj:
                return epsg, None
            
            else:
                return epsg, True
        else:
            return epsg, None
