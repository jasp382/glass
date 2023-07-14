"""
Join Bands
"""

def comp_bnds(rsts, outRst):
    """
    Composite Bands
    """
    
    import numpy as np
    from osgeo          import gdal, gdal_array
    from glass.prop.img import get_nd
    from glass.rd.rsrc  import imgsrc_to_num
    from glass.prop     import drv_name
    from glass.prop.prj import get_rst_epsg, epsg_to_wkt

    srcs = [gdal.Open(r) for r in rsts]
    
    # Get Arrays
    _as = [imgsrc_to_num(r) for r in srcs]
    
    # Get nodata values
    nds = [get_nd(r) for r in srcs]

    # Final NoData Value
    fnd = nds[0]

    # Replace NoData in all arrays
    for i in range(1, len(srcs)):
        np.place(_as[i], _as[i] == nds[i], fnd)
    
    # Assume that first raster is the template
    img_temp = srcs[0]
    geo_tran = img_temp.GetGeoTransform()
    
    dataType = gdal_array.NumericTypeCodeToGDALTypeCode(_as[0].dtype)
    rows, cols = _as[0].shape
    epsg = get_rst_epsg(rsts[0])
    
    # Create Output
    drv = gdal.GetDriverByName(drv_name(outRst))
    out = drv.Create(outRst, cols, rows, len(_as), dataType)
    out.SetGeoTransform(geo_tran)
    out.SetProjection(epsg_to_wkt(epsg))
    
    # Write all bands
    for i in range(len(_as)):
        outBand = out.GetRasterBand(i+1)
        outBand.SetNoDataValue(fnd)
        outBand.WriteArray(_as[i])
        
        outBand.FlushCache()
    
    return outRst

