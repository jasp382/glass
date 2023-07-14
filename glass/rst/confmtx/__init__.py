"""
Confusion matrix from Raster
"""

from osgeo    import gdal
import numpy  as np
import pandas as pd


def confmtx_fmrst(ref_rst, cls_rst):
    """
    Confusion matrix for two raster
    """

    from glass.cls.eval import get_measures_for_mtx

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

    return out_df



def bin_confmxt_fmrst(ref_rst, cls_rst):
    """
    Confusion matrix for two raster

    Assumes that we have only positives and
    negatives

    positives = 1
    negatives = 0
    """

    from glass.cls.eval import calc_confusion_measures

    l = ['TP', 'TN', 'FP', 'FN']

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

    df = pd.DataFrame(_ref_num, columns=['ref'])

    df['classi'] = _cls_num

    df['rid'] = df.index + 1

    # Get Confusion field
    # Get TP, TN, FP, FN
    df["confusion"] = np.where(
        (df.ref == 1) & (df.classi == 1), 'TP', np.where(
            (df.ref == 0) & (df.classi == 0), 'TN', np.where(
                (df.ref == 0) & (df.classi == 1), 'FP', 'FN'
            )
        )
    )

    # Table with TP, TN, FP, FN frequencies
    conftbl = pd.DataFrame()

    conftbl['nrows'] = df.groupby(['confusion'])['rid'].nunique()

    conftbl.reset_index(inplace=True)

    d = {}

    for idx, row in conftbl.iterrows():
        d[row['confusion']] = row.nrows
    
    for i in l:
        if i not in d:
            d[i] = 0
    
    # Get confusion matrix
    mtx = pd.DataFrame([
        [d['TP'], d['FP']],
        [d['FN'], d['TN']]
    ], columns=['positives', 'negatives'])

    # Get evaluation measures
    emeas = calc_confusion_measures(d)

    return mtx, emeas

