"""
Join Bands
"""

def comp_bnds(rsts, outRst):
    """
    Composite Bands
    """
    
    import numpy as np
    from osgeo          import gdal, gdal_array
    from glass.prop.img import img_stats, get_nd
    from glass.rd.rsrc  import imgsrc_to_num
    from glass.prop.df  import drv_name
    from glass.prop.prj import rst_epsg, epsg_to_wkt

    srcs = [gdal.Open(r) for r in rsts]
    
    # Get Arrays
    _as = [imgsrc_to_num(r) for r in srcs]
    
    # Get nodata values
    nds = [get_nd(r) for r in srcs]

    # Get Max value of all rasters
    stats = [img_stats(s) for s in srcs]

    # Decide ND
    ndvals = [True for s in srcs]
    for i in range(len(srcs)):
        for e in range(len(srcs)):
            if i == e:
                continue

            if nds[i] >= stats[e]['MIN'] and nds[i] <= stats[e]['MAX']:
                ndvals[i] = False
                break
    
    ndval = None
    for i in range(len(ndvals)):
        if ndvals[i]:
            ndval = nds[i]
            break
    
    if ndval == None:
        _max = [s["MAX"] for s in stats]
        ndval = max(_max) + 1
    
    
    # Assume that first raster is the template
    img_temp = srcs[0]
    geo_tran = img_temp.GetGeoTransform()
    
    dataType = gdal_array.NumericTypeCodeToGDALTypeCode(_as[0].dtype)
    rows, cols = _as[0].shape
    epsg = rst_epsg(rsts[0])
    
    # Create Output
    drv = gdal.GetDriverByName(drv_name(outRst))
    # TODO: Test it with other compress methods
    options = ["COMPRESS=LZW", "BIGTIFF=YES"]
    out = drv.Create(outRst, cols, rows, len(_as), dataType, options)
    out.SetGeoTransform(geo_tran)
    out.SetProjection(epsg_to_wkt(epsg))
    
    # Write all bands
    for i in range(len(_as)):
        np.place(_as[i], _as[i] == nds[i], ndval)

        outBand = out.GetRasterBand(i+1)
        outBand.SetNoDataValue(ndval)
        outBand.WriteArray(_as[i])
        
        outBand.FlushCache()
    
    return outRst

