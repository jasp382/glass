"""
Subset of Matrixes
"""

def clip_rst(raster, clipshp, outrst, nodataValue=None, api='gdal'):
    """
    Clip Raster using GDAL WARP
    """
    
    if api == 'gdal':
        from glass.pys    import execmd
        from glass.prop import drv_name

        nd = f"-dstnodata {str(nodataValue)}" if \
            nodataValue else ""
        
        outcmd = execmd((
            f"gdalwarp {nd}-cutline {clipshp} -crop_to_cutline "
            f"-of {drv_name(outrst)} {raster} -overwrite {outrst}"
        ))
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.clip', input=raster, output=outrst,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    elif api == 'grass':
        from glass.pys import execmd
        
        rcmd = execmd((
            f'r.clip input={raster} output={outrst} '
            '--overwrite --quiet'
        ))
    
    else:
        raise ValueError(f'API {api} is not available')
    
    return outrst


def grscliprst(in_rst, clip_ext, outrst):
    """
    Clip Raster using GRASS GIS
    """

    import os
    from glass.pys.oss    import fprop
    from glass.wenv.grs import run_grass
    from glass.wenv.grs import rst_to_region
    from glass.prop.prj import get_epsg

    # Get EPSG From Raster
    EPSG = get_epsg(in_rst)

    if not EPSG:
        raise ValueError(
            f'Cannot get EPSG code of Extent Template File ({in_rst})'
        )

    workspace = os.path.dirname(outrst)
    loc = 'loc_' + fprop(outrst, 'fn')

    # Create GRASS GIS Session
    gbase = run_grass(workspace, location=loc, srs=EPSG)

    import grass.script.setup as gsetup

    gsetup.init(gbase, workspace, loc, 'PERMANENT')

    # GRASS GIS modules
    from glass.it.rst import rst_to_grs, grs_to_rst, grs_to_mask

    # Add data to GRASS GIS
    rst = rst_to_grs(in_rst, fprop(in_rst, 'fn'), as_cmd=True)
    clip = rst_to_grs(clip_ext, fprop(clip_ext, 'fn'), as_cmd=True)

    # Set New region
    rst_to_region(clip)

    # Set Mask
    grs_to_mask(clip)

    # Export result
    return grs_to_rst(rst, outrst)

