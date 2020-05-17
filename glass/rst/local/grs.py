"""
Local Tools
"""

import os


def grs_combine(inRst, outRst, api="pygrass"):
    """
    Combine Rasters
    """
    
    if api == 'pygrass':
        from grass.pygrass.modules import Module
    
        c = Module(
            "r.cross", input=inRst, output=outRst, flags='z',
            overwrite=True, run_=False, quiet=True
        )
    
        c()
    
    elif api == "grass":
        from glass.pys import execmd
        
        rcmd = execmd((
            f"r.cross input={','.join(inRst)} output={outRst} "
            "-z --overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outRst



def combine_table(crst, cols_name, otbl, otxt=None):
    """
    Produce combine table
    """

    import pandas as pd
    from glass.prop.rst import raster_report
    from glass.wt import obj_to_tbl

    # Get Raster Report
    report = raster_report(
        crst,
        otxt if otxt else os.path.join(
            os.path.dirname(otbl),
            f'{crst}_report.txt'
        )
    )

    tbl, c = [], 0

    otxt = open(report, 'r')

    for l in otxt.readlines():
        try:
            if c >= 4:
                row = []

                pl = l.split('|')

                rval = pl[1]

                if rval == '*':
                    continue

                row.append(int(rval))

                cats = pl[2].split('; ')

                for cat in cats:
                    _cat = cat.split(' ')[1]

                    row.append(int(_cat))
                
                tbl.append(row)
            
            c += 1
        
        except: break
    
    odf = pd.DataFrame(tbl, columns=['value'] + cols_name)

    obj_to_tbl(odf, otbl)

    return otbl

