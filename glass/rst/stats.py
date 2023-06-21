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



def count_region_in_shape(folder, ref, out):
    """
    Count how many times a region appears in a set
    of ESRI Shapefiles

    e.g. Count how many times an area was burned
    """

    import os

    from glass.pys.oss  import lst_ff, fprop
    from glass.wenv.grs import run_grass

    # List burn areas shapes
    shps = lst_ff(folder, file_format='.shp')

    # Start GRASS GIS Session
    orst_name = fprop(out, 'fn')
    ws = os.path.dirname(out)
    loc = f'locprod_{orst_name}'

    gb = run_grass(ws, location=loc, srs=ref)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    from glass.it.shp    import shp_to_grs
    from glass.it.rst    import grs_to_rst
    from glass.rst.alg   import grsrstcalc
    from glass.rst.rcls  import null_to_value
    from glass.dtr.torst import grsshp_to_grsrst

    # For each shape
    # Import it to GRASS GIS
    # Convert to Raster
    # Null to zero
    rsts = []
    for shp in shps:
        gshp = shp_to_grs(shp)
    
        rshp = grsshp_to_grsrst(gshp, 1, f'rst_{gshp}')
    
        null_to_value(rshp, 0)
    
        rsts.append(rshp)
    
    # Sum all rasters
    frst = grsrstcalc(" + ".join(rsts), orst_name)

    # Export final raster
    grs_to_rst(frst, out, is_int=True)

    return out

