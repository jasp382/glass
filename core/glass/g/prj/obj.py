"""
Project Geometries
"""

def prj_ogrgeom(geom, in_epsg, out_epsg, api='ogr'):
    """
    Project OGR Geometry

    API Options:
    * ogr;
    * shapely or shply;
    """

    from osgeo import ogr
    

    if api == 'ogr':
        from glass.g.prop.prj import get_trans_param

        newg = ogr.CreateGeometryFromWkt(geom.ExportToWkt())

        newg.Transform(get_trans_param(in_epsg, out_epsg))
    
    elif api == 'shapely' or api == 'shply':
        import pyproj
        from shapely.ops import transform
        from shapely.wkt import loads

        shpgeom = loads(geom.ExportToWkt())

        srs_in = pyproj.Proj('epsg:' + str(in_epsg))
        srs_ou = pyproj.Proj('epsg:' + str(out_epsg))

        proj = pyproj.Transformer.from_proj(
            srs_in, srs_ou, always_xy=True
        ).transform

        newg = transform(proj, shpgeom)
        newg = ogr.CreateGeometryFromWkt(newg.wkt)
    
    else:
        raise ValueError(f'API {api} is not available')

    return newg


def df_prj(df, out_epsg):
    """
    Project Geometries in Pandas Dataframe
    """

    out_df = df.to_crs(f'EPSG:{str(out_epsg)}')

    return out_df
