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



def combine_report_to_df(crst, cols_name, otxt=None):
    """
    Produce combine table and return it in DataFrame
    """

    import pandas as pd
    from glass.prop.rst import raster_report
    

    # Get Raster Report
    report = raster_report(
        crst,
        otxt if otxt else os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
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

    return odf


def combine_table(cmbrst, cols, otbl, out_txt=None):
    """
    Produce combine raster table and save it in a xlsx file
    """

    from glass.wt import obj_to_tbl

    df = combine_report_to_df(cmbrst, cols, otxt=out_txt)

    obj_to_tbl(df, otbl)

    return otbl

