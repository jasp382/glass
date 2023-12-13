"""
Local Tools
"""

import os

def combine(rsts, orst, api="grass"):
    """
    Combine Rasters
    """

    if api == "grass" or api == "pygrass":
        from glass.pys.oss import fprop
        from glass.pys.tm import now_as_str
        from glass.wenv.grs import run_grass

        # Create GRASS GIS Session
        ws, loc = os.path.dirname(orst), now_as_str(utc=True)

        gb = run_grass(ws, location=loc, srs=rsts[0])

        import grass.script.setup as gsetup

        gsetup.init(gb, ws, loc, 'PERMANENT')

        from glass.it.rst import grs_to_rst, rst_to_grs
        from glass.rst.local.grs import grs_combine, combine_table

        grst = [rst_to_grs(r) for r in rsts]

        # Combine Rasters
        cmb = grs_combine(grst, fprop(orst, 'fn'), api=api)

        # Get Combine table
        cmbtxt = os.path.join(ws, loc, f'{cmb}.txt')
        ct = combine_table(cmb, grst, os.path.join(
            ws, f'{cmb}.xlsx'
        ), otxt=cmbtxt)

        # Export Raster
        grs_to_rst(
            cmb, orst, rtype=int,
            as_cmd=True if api == 'grass' else None
        )
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return orst

