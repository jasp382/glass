"""
Python data to SHP
"""

def df_to_shp(indf, outShp, layername=None):
    """
    Pandas Dataframe to Geospatial file
    """

    from glass.prop.df import drv_name

    drv = drv_name(outShp)

    if drv == 'GPKG' and layername:
        indf.to_file(outShp, driver=drv, layer=layername)
    
    else:
        indf.to_file(outShp)
    
    return outShp


def obj_to_shp(dd, geomkey, srs, outshp, lyrname=None, iswkt=None, cols=None):
    """
    Write geoobject in shapefile
    """

    if not iswkt:
        from glass.it.pd import df_to_geodf as obj_to_geodf
    
    else:
        from glass.it.pd import obj_to_geodf

        if cols and geomkey not in cols:
            cols.append(geomkey)
    
    geodf = obj_to_geodf(dd, geomkey, srs, cols=cols)
    
    return df_to_shp(geodf, outshp, layername=lyrname)


