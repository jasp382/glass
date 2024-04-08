"""
GRASS GIS tools
"""


def count_regionshp(shps, ogrs, return_prob=None, nnprob=None):
    """
    Count how many times a region appears in a set
    of ESRI Shapefiles

    if returnprob:
        return probability n_time_burned/n_years if one shape by year

    e.g. Count how many times an area was burned
    """

    from glass.it.shp        import shp_to_grs
    from glass.rst.alg       import grsrstcalc
    from glass.rst.rcls.grs  import null_to_value
    from glass.dtt.rst.torst import grsshp_to_grsrst

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
    sumrst = " + ".join(rsts)
    deno = "" if not return_prob else \
        f" / {str(len(shps)) if not nnprob else str(nnprob)}.0"
    exp = f"({sumrst}){deno}"
    
    frst = grsrstcalc(exp, ogrs)

    return ogrs

