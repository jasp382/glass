"""
Subset of Matrixes
"""

def clip_rst(raster, clipShp, outRst, nodataValue=None, api='gdal'):
    """
    Clip Raster using GDAL WARP
    """
    
    if api == 'gdal':
        from glass.pyt            import execmd
        from glass.geo.gt.prop.ff import drv_name
    
        outcmd = execmd((
            "gdalwarp {ndata}-cutline {clipshp} -crop_to_cutline "
            "-of {ext} {inraster} -overwrite {outrst}"
        ).format(
            clipshp=clipShp, inraster=raster, outrst=outRst,
            ext=drv_name(outRst),
            ndata="-dstnodata {} ".format(
                str(nodataValue)) if nodataValue else ""
        ))
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.clip', input=raster, output=outRst,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    elif api == 'grass':
        from glass.pyt import execmd
        
        rcmd = execmd('r.clip input={} output={} --overwrite --quiet'.format(
            raster, outRst
        ))
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return outRst
