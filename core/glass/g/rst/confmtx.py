"""
Confusion matrix from Raster
"""

def confmtx_twrst(ref_rst, cls_rst, out_tbl):
    """
    Confusion matrix for two raster
    """

    from osgeo          import gdal
    import numpy        as np
    import pandas       as pd
    from glass.ng.cls.eval import get_measures_for_mtx
    from glass.ng.wt       import obj_to_tbl

    ref_img = gdal.Open(ref_rst, gdal.GA_ReadOnly)
    cls_img = gdal.Open(cls_rst, gdal.GA_ReadOnly)

    ref_nd = ref_img.GetRasterBand(1).GetNoDataValue()
    cls_nd = cls_img.GetRasterBand(1).GetNoDataValue()

    # Data to Array
    ref_num = ref_img.GetRasterBand(1).ReadAsArray()
    cls_num = cls_img.GetRasterBand(1).ReadAsArray()

    # Reshape Array
    ref_num = ref_num.reshape(ref_num.shape[0] * ref_num.shape[1])
    cls_num = cls_num.reshape(cls_num.shape[0] * cls_num.shape[1])

    # Delete NoData Values from both array's
    ref_num_ = ref_num[ref_num != ref_nd]
    cls_num_ = cls_num[ref_num != ref_nd]

    _ref_num = ref_num_[cls_num_ != cls_nd]
    _cls_num = cls_num_[cls_num_ != cls_nd]

    # Get classes of both arrays
    ref_cls = np.unique(_ref_num)
    cls_cls = np.unique(_cls_num)
    ref_cls_ = list(np.sort(np.unique(np.append(ref_cls, cls_cls))))

    # Matrix classes
    mtx_coords = {}

    i = 1
    for v in ref_cls_:
        for v_ in ref_cls_:
            mtx_coords[(v, v_)] = i

            i += 1
    
    comp_num = np.zeros(_ref_num.shape, dtype=_ref_num.dtype)

    for k in mtx_coords:
        np.place(comp_num, (_ref_num == k[1]) & (_cls_num == k[0]), mtx_coords[k])
    
    id_mtx = list(np.unique(comp_num))

    freq = np.bincount(comp_num)
    freq = list(freq[freq != 0])

    freq_d = {id_mtx[i] : freq[i] for i in range(len(id_mtx))}

    mtx_values = {}
    for k in mtx_coords:
        if mtx_coords[k] in id_mtx:
            mtx_values[k] = freq_d[mtx_coords[k]]
        else:
            mtx_values[k] = 0
    
    mtx_lst = []

    for v in ref_cls_:
        r = []
        for v_ in ref_cls_:
            r.append(mtx_values[(v, v_)])
        mtx_lst.append(r)
    
    mtx_df = pd.DataFrame(mtx_lst, columns=ref_cls_, index=ref_cls_)

    mtx_df.reset_index(inplace=True)
    mtx_df.rename(columns={'index' : 'class'}, inplace=True)
    out_df = get_measures_for_mtx(mtx_df, 'class')

    obj_to_tbl(out_df, out_tbl)

    return out_tbl


def confmtx_fm_pntsample(pnt, idcol, refcol, rst, clscol, out_mtx):
    """
    Confusion matrix using classified raster and point feature class with
    reference values
    """

    import pandas as pd
    import numpy as np
    from glass.g.rd.shp    import shp_to_obj
    from glass.ng.wt       import obj_to_tbl
    from glass.ng.cls.eval import get_measures_for_mtx
    from glass.g.tbl.col   import add_fields, update_cols
    from glass.g.smp       import rst_val_to_points

    # Extract raster values to points
    rval = rst_val_to_points(pnt, rst)

    # Add field to shape
    add_fields(pnt, {clscol : 'INTEGER'}, api='ogrinfo')

    # Update point table
    edit = {}
    for k in rval:
        if int(rval[k]) not in edit:
            edit[int(rval[k])] = ["{}={}".format(idcol, str(k))]
        else:
            edit[int(rval[k])].append("{}={}".format(idcol, str(k)))
    
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

