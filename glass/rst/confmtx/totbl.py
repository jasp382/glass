"""
Confusion matrix from Raster to Table file
"""

from glass.rst.confmtx import confmtx_fmrst


def confmtx_twrst(ref_rst, cls_rst, out_tbl):
    """
    Confusion matrix for two raster
    """

    from glass.wt import obj_to_tbl

    out_df = confmtx_fmrst(ref_rst, cls_rst)

    obj_to_tbl(out_df, out_tbl)

    return out_tbl


def confmtx_fm_pntsample(pnt, idcol, refcol, rst, clscol, out_mtx):
    """
    Confusion matrix using classified raster and point feature class with
    reference values
    """

    import pandas       as pd
    import numpy        as np
    from glass.rd.shp   import shp_to_obj
    from glass.wt       import obj_to_tbl
    from glass.cls.eval import get_measures_for_mtx
    from glass.tbl.col  import add_fields, update_cols
    from glass.smp      import rst_val_to_points

    # Extract raster values to points
    rval = rst_val_to_points(pnt, rst)

    # Add field to shape
    add_fields(pnt, {clscol : 'INTEGER'}, api='ogrinfo')

    # Update point table
    edit = {}
    for k in rval:
        if int(rval[k]) not in edit:
            edit[int(rval[k])] = [f"{idcol}={str(k)}"]
        else:
            edit[int(rval[k])].append(f"{idcol}={str(k)}")
    
    update_cols(pnt, clscol, edit)

    # Produce confusion matrix
    df = shp_to_obj(pnt)

    df[clscol] = df[clscol].astype(int)
    df[refcol] = df[refcol].astype(int)

    # Remove nan values
    df = df[pd.notnull(df[refcol])]
    df = df[pd.notnull(df[clscol])]

    # Get rows and Cols
    rows = df[clscol].unique()
    cols = df[refcol].unique()
    refval = list(np.sort(np.unique(np.append(rows, cols))))

    # Produce matrix
    outdf = []
    for row in refval:
        newcols = [row]
        for col in refval:
            newdf = df[(df[clscol] == row) & (df[refcol] == col)]

            if not newdf.shape[0]:
                newcols.append(0)
            
            else:
                newcols.append(newdf.shape[0])
        
        outdf.append(newcols)
    
    outcols = ['class'] + refval

    outdf = pd.DataFrame(outdf, columns=outcols)

    out_df = get_measures_for_mtx(outdf, 'class')

    return obj_to_tbl(out_df, out_mtx)

