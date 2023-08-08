"""
Resample Raster Files
"""


def match_cellsize_and_clip(rstBands, refRaster, outFolder,
                            clipgeo=None, isint=None, ws=None):
    """
    Resample images to make them with the same resolution and clip
    
    Good to resample Sentinel bands with more than 10 meters.
    
    Dependencies: 
    * GRASS GIS;
    * GDAL/OGR.
    """
    
    import os
    from glass.prop.df  import is_rst
    from glass.prop.prj import rst_epsg
    from glass.wenv.grs import run_grass
    from glass.pys.oss  import fprop, mkdir
    from glass.pys.tm   import now_as_str
    
    # Check if outfolder exists
    if not os.path.exists(outFolder):
        mkdir(outFolder, overwrite=None)
    
    # Get EPSG from refRaster
    epsg = rst_epsg(refRaster, returnIsProj=None)
    
    """
    Start GRASS GIS Session
    """
    ws = mkdir(os.path.join(outFolder, now_as_str())) \
        if not ws else ws
    grsb = run_grass(
        ws, grassBIN='grass78', location='resample',
        srs=epsg
    )
    
    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, 'resample', 'PERMANENT')
    
    """
    Import packages related with GRASS GIS
    """
    from glass.it.rst    import rst_to_grs, grs_to_rst, grs_to_mask
    from glass.wenv.grs  import rst_to_region
    from glass.it.shp    import shp_to_grs
    from glass.dtt.torst import grsshp_to_grsrst as shp_to_rst
    
    # Send Ref Raster to GRASS GIS and set region
    extRst = rst_to_grs(refRaster, 'ext_rst')
    rst_to_region(extRst)
    
    # Import all bands in rstBands
    grs_bands = [rst_to_grs(i, fprop(i, 'fn')) for i in rstBands]
    
    if clipgeo:
        clip_is_rst = is_rst(clipgeo)

        # Add clipgeo to GRASS
        if not clip_is_rst:
            grs_clip = shp_to_grs(clipgeo, fprop(clipgeo, 'fn'), asCMD=True)

            # SHP to Raster
            rst_clip = shp_to_rst(
                grs_clip, 1, f'rst_{grs_clip}',
                cmd=True
            )
        
        else:
            rst_clip = rst_to_grs(clipgeo, fprop(clipgeo, 'fn'))

        # Set region using
        rst_to_region(rst_clip)

        # Set mask
        grs_to_mask(rst_clip)
    
    # Export bands
    return [grs_to_rst(
        i, os.path.join(outFolder, i + '.tif'),
        is_int=int if isint else float
    ) for i in grs_bands]


def resample_by_majority(refrst, valrst, out_rst):
    """
    Resample valrst based on refrst:
        Get Majority value of valrst for each cell in refrst

    Useful when ref raster has cellsize greater
    than value raster.

    TODO: Valrst must be of int type
    """

    import numpy          as np
    from osgeo            import gdal
    from glass.prop.img import get_cell_size, get_nd
    from glass.wt.rst   import obj_to_rst

    # Data to Array
    if type(refrst) == gdal.Dataset:
        refsrc = refrst
    
    else:
        refsrc = gdal.Open(refrst)
    
    if type(valrst) == gdal.Dataset:
        valsrc = valrst
    else:
        valsrc = gdal.Open(valrst)

    refnum = refsrc.ReadAsArray()
    valnum = valsrc.ReadAsArray()

    # Get Ref shape
    ref_shape = refnum.shape

    # in a row, how many cells valnum are for each refnum cell
    refcs = int(get_cell_size(refsrc)[0])
    valcs = int(get_cell_size(valsrc)[0])
    dcell = int(refcs / valcs)

    # Valnum must be of int type

    # Create generalized/resampled raster
    resnum = np.zeros(ref_shape, dtype=valnum.dtype)

    for row in range(ref_shape[0]):
        for col in range(ref_shape[1]):
            resnum[row, col] = np.bincount(
                valnum[row*dcell:row*dcell+dcell, col*dcell : col*dcell+dcell].reshape(dcell*dcell)
            ).argmax()
    
    # Export out raster
    return obj_to_rst(resnum, out_rst, refsrc, noData=get_nd(valsrc))

