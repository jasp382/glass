"""
Something to Geom
"""


def coords_to_boundary(topLeft, lowerRight, epsg, outEpsg=None):
    """
    Top Left and Lower Right to Boundary
    """

    from osgeo import ogr
    from glass.geo.obj.g import create_polygon

    boundary_points = [
        (   topLeft[0],    topLeft[1]),
        (lowerRight[0],    topLeft[1]),
        (lowerRight[0], lowerRight[1]),
        (   topLeft[0], lowerRight[1]),
        (   topLeft[0],    topLeft[1])
    ]

    # Create polygon
    polygon = create_polygon(boundary_points)

    # Convert SRS if outEPSG
    if outEpsg and epsg != outEpsg:
        from glass.geo.obj.prj import prj_ogrgeom

        poly = prj_ogrgeom(polygon, epsg, outEpsg)

        return poly
    else:
        return polygon


def shpext_to_boundary(in_shp, out_srs=None):
    """
    Read one feature class extent and create a boundary with that
    extent
    """

    from glass.geo.prop.ext import get_ext
    from glass.geo.obj.g    import create_polygon

    # Get Extent
    ext = get_ext(in_shp)

    # Create points of the new boundary based on the extent
    boundary_points = [
        (ext[0], ext[3]), (ext[1], ext[3]),
        (ext[1], ext[2]), (ext[0], ext[2]), (ext[0], ext[3])
    ]
    polygon = create_polygon(boundary_points)

    if out_srs:
        from glass.geo.prop.prj import get_epsg_shp

        in_srs = get_epsg_shp(in_shp)

        if in_srs != out_srs:
            from glass.geo.obj.prj import prj_ogrgeom

            poly = prj_ogrgeom(polygon, in_srs, out_srs,
                api='shply')

            return poly
        
        else:
            return polygon
    else:
        return polygon


def osm_extract(in_osm, out_osm, left, right, bottom, top):
    """
    Extract OSM Data from a xml/pbf with osmosis using some bounding box
    """

    import os
    from glass.pys  import execmd

    in_fn, in_ff = fn, ff = os.path.splitext(os.path.basename(in_osm))
    out_fn, out_ff = fn, ff = os.path.splitext(os.path.basename(out_osm))

    cmd = (
        "osmosis --read-{_f} {dtparse}file={_in} "
        "--bounding-box top={t} left={l} bottom={b} right={r} "
        "--write-{outext} file={_out}"
    ).format(
        _f='pbf' if in_ff == '.pbf' else 'xml', _in=in_osm,
        t=str(top), l=str(left), b=str(bottom), r=str(right),
        _out=out_osm, outext='pbf' if out_ff == '.pbf' else 'xml',
        dtparse="" if in_ff == '.pbf' else 'enableDataParsing=no '
    )

    rcmd = execmd(cmd)

    return out_osm

