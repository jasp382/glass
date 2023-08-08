"""
Reference Data for Training Models Purposes 
"""

def random_select_from_ref(train_ref, class_col, class_proportion,
                           ref_rst, sampledim, clsmin, orst, clouds=None):
    """
    Select random cells from a reference file
    with LULC classes distribution

    Use a stratified approach
    """

    import os
    from glass.pys.oss  import fprop
    from glass.pys.tm   import now_as_str
    from glass.smp      import proprndcells_to_rst
    from glass.wenv.grs import run_grass
    from glass.prop     import is_shp

    # Create GRASS GIS Session
    ws, loc = os.path.dirname(orst), f"loc_{now_as_str()}"

    grsb = run_grass(ws, location=loc, srs=ref_rst)
    
    import grass.script.setup as gsetup
    
    gsetup.init(grsb, ws, loc, 'PERMANENT')

    from glass.it.shp import shp_to_grs
    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.dtt.torst import grsshp_to_grsrst
    from glass.rst.alg  import grsrstcalc

    # Check if train ref is raster or not
    isshp = is_shp(train_ref)

    if isshp:
        # Add Train Reference ESRI Shapefile to GRASS GIS
        train_shp = shp_to_grs(train_ref)

        # Train reference to Raster
        train_rst = grsshp_to_grsrst(train_shp, class_col, f"rst_{train_shp}")
    
    else:
        train_rst = rst_to_grs(train_ref)
    
    # Remove clouds if necessary

    if clouds:
        _clouds = rst_to_grs(clouds)
    
        train_rst = grsrstcalc(f"{train_rst} + {_clouds}", f"f_{train_rst}")
    
    # Export result
    tres = grs_to_rst(train_rst, os.path.join(
        ws, loc,
        f"tmp_{fprop(orst, 'fn')}.tif"
    ), is_int=True)

    # Select random sample
    proprndcells_to_rst(
        tres, class_proportion, orst,
        sampledim, cls_sample_min=clsmin
    )

    return orst

