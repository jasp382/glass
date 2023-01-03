"""
Raster statitics
"""

def rst_mean(rsts, out_rst):
    """
    Return rasters mean
    """

    import numpy as np
    from osgeo import gdal
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
    return obj_to_rst(num_out, out_rst, src_rst[0], noData=nd_out)

