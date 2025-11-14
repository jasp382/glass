"""
Merge, combine and mosaic
"""

import os

from glass.wenv.grs import grass_session
from glass.pys.tm   import now_as_str
from glass.pys.oss  import lst_ff, fprop
from glass.prop.df   import is_shp
from glass.prop.prj import get_epsg
from glass.prop.ext  import get_ext
from glass.wenv.grs      import shp_to_region, align_region, rst_to_region
from glass.dtt.toshp import coords_to_boundshp
from glass.it.rst import rst_to_grs, grs_to_rst, grs_to_mask
from glass.it.shp import shp_to_grs
from glass.rst.mos.grs import rseries
from glass.dtt.rst.torst import grsshp_to_grsrst as shp_to_rst



def fullgrass_rseries(ifolder, refrst, method, orst):
    """
    R. Series using grass
    """

    loc = now_as_str()

    gbase = grass_session(ifolder, loc=loc, srs=refrst)

    rsts = [rst_to_grs(r) for r in lst_ff(ifolder, file_format='.tif')]

    prst = rseries(rsts, fprop(orst, 'fn'), method, as_cmd=True)

    grs_to_rst(prst, orst)

    return orst


def fullgrass_rpatch(rsts:list[str], refrst:str, out:str, nthreads=1,
                     ndVal=None, dType=None, loc_bname=None, mask=None):
    """
    R.Patch using GRASS GIS
    """

    loc = now_as_str() if not loc_bname else f'{loc_bname}_{now_as_str()}'
    ws = os.path.dirname(out)
    gbase = grass_session(ws, loc=loc, srs=refrst)

    from glass.rst.mos.grs import rsts_to_mosaic

    grsts = [rst_to_grs(r) for r in rsts]

    gout = rsts_to_mosaic(grsts, fprop(out, 'fn'), _nprocs=nthreads)

    if mask:
        epsg = get_epsg(refrst)
        # Check if mask is a shape
        # If not, convert to vector

        if not is_shp(mask):
            left, right, bottom, top = get_ext(mask, oepsg=epsg)

            maskshp = coords_to_boundshp(
                (left, top),
                (right, bottom), epsg,
                os.path.join(ws, loc, 'maskshape.shp')
            )
        
        else:
            maskshp = mask

        # Import Mask
        clip_shp = shp_to_grs(maskshp, asCMD=True)

        # Change region
        shp_to_region(clip_shp)

        # Align region with reference raster
        gref = rst_to_grs(refrst)
        align_region(gref)

        maskrst = shp_to_rst(
            clip_shp, 1, f'rst_{clip_shp}',
            cmd=True
        )

        rst_to_region(maskrst)
        grs_to_mask(maskrst)

    grs_to_rst(
        gout, out, as_cmd=True,
        dtype=dType, nodata=ndVal
    )

    return out


def bnds_to_mosaic(bands, outdata, ref_raster, loc=None):
    """
    Satellite image To mosaic
    
    bands = {
        'bnd_2' : [path_to_file, path_to_file],
        'bnd_3' : [path_to_file, path_to_file],
        'bnd_4' : [path_to_file, path_to_file],
    }
    """
    
    """
    Start GRASS GIS Session
    """
    
    from glass.prop.prj import rst_epsg

    # Get EPSG from refRaster
    epsg = rst_epsg(ref_raster, returnIsProj=None)
    
    LOC = loc if loc else 'gr_loc'
    grass_base = grass_session(outdata, loc=LOC, srs=epsg)
    
    # ************************************************************************ #
    # GRASS MODULES #
    # ************************************************************************ #
    from glass.it.rst import rst_to_grs, grs_to_rst
    from glass.wenv.grs import rst_to_region
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(ref_raster, 'extent_raster')
    rst_to_region(extRst)
    # ************************************************************************ #
    # SEND DATA TO GRASS GIS #
    # ************************************************************************ #
    grs_bnds = {}
    
    for bnd in bands:
        l= []
        for b in bands[bnd]:
            bb = rst_to_grs(b, fprop(b, 'fn'))
            l.append(bb)
        
        grs_bnds[bnd] = l
    # ************************************************************************ #
    # PATCH bands and export #
    # ************************************************************************ #
    for bnd in grs_bnds:
        mosaic_band = rseries(grs_bnds[bnd], bnd, 'maximum')
        
        grs_bnds[bnd] = grs_to_rst(mosaic_band, os.path.join(
            outdata, mosaic_band + '.tif'
        ), as_cmd=True)
    
    return grs_bnds

