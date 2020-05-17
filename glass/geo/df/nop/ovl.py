"""
Subset of Matrixes
"""

def clip_rst(raster, clipShp, outRst, nodataValue=None, api='gdal'):
    """
    Clip Raster using GDAL WARP
    """
    
    if api == 'gdal':
        from glass.pys         import execmd
        from glass.geo.prop.df import drv_name
    
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
        from glass.pys  import execmd
        
        rcmd = execmd('r.clip input={} output={} --overwrite --quiet'.format(
            raster, outRst
        ))
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return outRst


def grscliprst(in_rst, clip_ext, outrst):
    """
    Clip Raster using GRASS GIS
    """

    import os
    from glass.pys.oss import fprop
    from glass.geo.wenv.grs import run_grass
    from glass.geo.wenv.grs import rst_to_region
    from glass.geo.prop.prj import get_epsg

    # Get EPSG From Raster
    EPSG = get_epsg(in_rst)
    if not EPSG:
        raise ValueError(
            'Cannot get EPSG code of Extent Template File ({})'.format(
                in_rst
            )
        )

    workspace = os.path.dirname(outrst)
    loc = 'loc_' + fprop(outrst, 'fn')

    # Create GRASS GIS Session
    gbase = run_grass(workspace, location=loc, srs=EPSG)

    import grass.script.setup as gsetup

    gsetup.init(gbase, workspace, loc, 'PERMANENT')

    # GRASS GIS modules
    from glass.dct.geo.torst import rst_to_grs, grs_to_rst, grs_to_mask

    # Add data to GRASS GIS
    rst = rst_to_grs(in_rst, fprop(in_rst, 'fn'), as_cmd=True)
    clip = rst_to_grs(clip_ext, fprop(clip_ext, 'fn'), as_cmd=True)

    # Set New region
    rst_to_region(clip)

    # Set Mask
    grs_to_mask(clip)

    # Export result
    return grs_to_rst(rst, outrst)

