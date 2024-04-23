"""
Likelihood Ratio Method Implementation
"""

import os


def grass_lri(events, vars, refrst, out):
    """
    Likelihood Ratio Method using GRASS GIS

    vars: dict = {
        var_slug : path_to_raster,
        var_slug : {
            path_to_var : weight, ...
        }, ...
    }
    """

    from glass.prop.df       import is_rst
    from glass.wenv.grs      import run_grass
    from glass.pys.oss       import lst_ff, fprop
    from glass.pys.tm        import now_as_str
    from glass.prop.rst      import count_cells

    ws, loc = os.path.dirname(out), now_as_str(utc=True)

    # Start GRASS GIS Session
    gb = run_grass(ws, grassBIN='grass78', location=loc, srs=refrst)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    from glass.it.rst import rst_to_grs, grs_to_rst
    from glass.it.shp import shp_to_grs
    from glass.dtt.rst.torst import grsshp_to_grsrst
    from glass.rst.zon.grs import rstatszonal
    from glass.rst.alg import grsrstcalc

    # Events to Raster and to GRASS GIS
    isrst = is_rst(events)

    if isrst:
        gevents = rst_to_grs(events, as_cmd=True)
        fevents = events
    
    else:
        evshp = shp_to_grs(events, asCMD=True)

        # To Raster
        gevents = grsshp_to_grsrst(evshp, 1, f'rst_{evshp}', cmd=True)
        fevents = grs_to_rst(
            gevents,
            os.path.join(ws, loc, f'{gevents}.tif'),
            as_cmd=True, rtype=int
        )

    # Count region cells
    ncells = count_cells(refrst)

    # Count burned cells
    bcells = count_cells(fevents)

    # Create RI Rasters
    def get_lri(factor, lri):
        # Count number of burned cells by class
        burn_cells_cls = rstatszonal(factor, gevents, 'count', f"burn_{factor}")
    
        # Count number of cells by class
        cells_cls = rstatszonal(factor, factor, 'count', f"class_{factor}")
    
        # Create LRI raster for the given factor
        _lri = grsrstcalc((
            f"(double({burn_cells_cls}) / double({cells_cls}))"
            f" / "
            f"({str(int(bcells))}.0 / {str(int(ncells))}.0)"
        ), lri)

        return lri
    
    for k in vars:
        if type(vars[k]) == dict:
            exp, y = [], 0
            
            for _k in vars[k]:
                _v = rst_to_grs(_k, as_cmd=True)

                _lri = get_lri(_v, f'wlri_{_v}')

                y += vars[k][_k]

                exp.append(f"({_lri} * {str(vars[k][_k])})")
            
            # Sum all
            vars[k] = grsrstcalc(
                f"({' + '.join(exp)}) / {str(y)}",
                f'lri_{k}'
            )
            
        else:
            _v = rst_to_grs(vars[k], as_cmd=True)
            vars[k] = get_lri(_v, f'lri_{k}')
    
    # Sum everything
    frst = grsrstcalc(
        f" + ".join(list(vars.values())),
        fprop(out, 'fn')
    )

    # Export result
    grs_to_rst(frst, out, rtype=float)

    return out

