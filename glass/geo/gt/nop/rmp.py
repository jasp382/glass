"""
Resample Raster Files
"""

def match_cellsize_and_clip(rstBands, refRaster, outFolder,
                            clipShp=None):
    """
    Resample images to make them with the same resolution and clip
    
    Good to resample Sentinel bands with more than 10 meters.
    
    Dependencies: 
    * GRASS GIS;
    * GDAL/OGR.
    """
    
    import os
    from glass.geo.gt.prop.prj import get_rst_epsg
    from glass.geo.gt.wenv.grs import run_grass
    from glass.pyt.oss     import fprop, mkdir
    
    # Check if outfolder exists
    if not os.path.exists(outFolder):
        mkdir(outFolder, overwrite=None)
    
    # Get EPSG from refRaster
    epsg = get_rst_epsg(refRaster, returnIsProj=None)
    
    """
    Start GRASS GIS Session
    """
    GRS_WORKSPACE = mkdir(os.path.join(outFolder, 'grswork'))
    grsb = run_grass(
        GRS_WORKSPACE, grassBIN='grass78', location='resample',
        srs=epsg
    )
    
    import grass.script as grass
    import grass.script.setup as gsetup
    
    gsetup.init(grsb, GRS_WORKSPACE, 'resample', 'PERMANENT')
    
    """
    Import packages related with GRASS GIS
    """
    from glass.geo.gt.torst     import rst_to_grs, grs_to_rst
    from glass.geo.gt.wenv.grs  import rst_to_region
    from glass.geo.gt.toshp.cff import shp_to_grs
    from glass.geo.gt.torst     import shp_to_rst, grs_to_mask
    
    # Send Ref Raster to GRASS GIS and set region
    extRst = rst_to_grs(refRaster, 'ext_rst')
    rst_to_region(extRst)
    
    # Import all bands in rstBands
    grs_bands = [rst_to_grs(i, fprop(i, 'fn')) for i in rstBands]
    
    if clipShp:
        # Add clipShp to GRASS
        grs_clip = shp_to_grs(clipShp, fprop(clipShp, 'fn'), asCMD=True)

        # SHP to Raster
        rstClip = shp_to_rst(
            grs_clip, 1, None, 0, 'rst_' + grs_clip,
            api='grass'
        )

        # Set region using
        rst_to_region(rstClip)

        # Set mask
        grs_to_mask(rstClip)
    
    # Export bands
    return [grs_to_rst(
        i, os.path.join(outFolder, i + '.tif')
    ) for i in grs_bands]


def resample_by_majority(refrst, valrst, out_rst):
    """
    Resample valrst based on refrst:
        Get Majority value of valrst for each cell in refrst

    Useful when ref raster has cellsize greater
    than value raster.

    TODO: Valrst must be of int type
    """

    import numpy         as np
    from osgeo           import gdal
    from glass.geo.gm.prop.img import get_cell_size, get_nd
    from glass.geo.gt.torst    import obj_to_rst

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

