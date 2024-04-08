"""
Raster statitics
"""

def rst_mean(rsts, out_rst):
    """
    Return rasters mean
    """

    import numpy as np
    from osgeo import gdal
    from glass.prop.img import rst_epsg
    from glass.wt.rst import obj_to_rst

    # Open images
    src_rst = [gdal.Open(i, gdal.GA_ReadOnly) for i in rsts]

    # To Array
    num_rst = [s.GetRasterBand(1).ReadAsArray() for s in src_rst]

    # Sum all rasters
    num_out = num_rst[0]
    for i in range(1, len(num_rst)):
        num_out = num_out + num_rst[i]
    
    # Get Mean
    num_out = num_out / len(rsts)

    # Place NoDatas
    nd_out = np.amin(num_out) - 1
    for r in range(len(src_rst)):
        nd_val = src_rst[r].GetRasterBand(1).GetNoDataValue()

        np.place(num_out, num_rst[r] == nd_val, nd_out)
    
    # Export result
    return obj_to_rst(
        num_out, out_rst,
        src_rst[0].GetGeoTransform(),
        rst_epsg(src_rst[0]), noData=nd_out
    )



def count_region_in_shape(folder, ref, out, returnprob=None, nprob=None):
    """
    Count how many times a region appears in a set
    of ESRI Shapefiles

    if returnprob:
        return probability n_time_burned/n_years if one shape by year

    e.g. Count how many times an area was burned
    """

    import os

    from glass.pys.oss       import lst_ff, fprop
    from glass.pys.tm        import now_as_str
    from glass.wenv.grs      import grass_session
    from glass.rst.stats.grs import count_regionshp

    # List burn areas shapes
    shps = lst_ff(folder, file_format='.shp')

    # Start GRASS GIS Session
    orst_name = fprop(out, 'fn')
    ws, loc = os.path.dirname(out), now_as_str()

    gb = grass_session(ws, loc=loc, srs=ref)
    
    from glass.it.rst        import grs_to_rst

    frst = count_regionshp(
        shps, fprop(out, 'fn'),
        return_prob=returnprob,
        nnprob=nprob
    )

    # Export final raster
    grs_to_rst(
        frst, out,
        dtype="UInt16" if not returnprob else "Float64"
    )

    return out

