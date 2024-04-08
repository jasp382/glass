"""
Confusion matrix from Raster
"""

from osgeo    import gdal
import numpy  as np
import pandas as pd


def confmtx_fmrst(ref_rst, cls_rst, class_labels=None):
    """
    Confusion matrix for two raster
    """

    from glass.cls.eval import get_measures_for_mtx

    ref_img = gdal.Open(ref_rst, gdal.GA_ReadOnly)
    cls_img = gdal.Open(cls_rst, gdal.GA_ReadOnly)

    # Check Shapes
    refshp = (ref_img.RasterYSize, ref_img.RasterXSize)
    clsshp = (cls_img.RasterYSize, cls_img.RasterXSize)

    if refshp != clsshp:
        raise ValueError((
            'Reference Raster and Classification '
            'Raster have different shape'
        ))

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

    if class_labels:
        labels = [class_labels[c] for c in ref_cls_]
    
    else:
        labels = ref_cls_
    
    mtx_df = pd.DataFrame(mtx_lst, columns=labels)

    mtx_df["class"] = labels

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

    from glass.cls.eval.obj import calc_confusion_measures

    l = ['TP', 'TN', 'FP', 'FN']

    ref_ds = gdal.Open(ref_rst, gdal.GA_ReadOnly)
    cls_ds = gdal.Open(cls_rst, gdal.GA_ReadOnly)

    ref_band = ref_ds.GetRasterBand(1)
    cls_band = cls_ds.GetRasterBand(1)

    ref_nd = ref_band.GetNoDataValue()
    cls_nd = cls_band.GetNoDataValue()

    xsize, ysize = ref_band.XSize, ref_band.YSize

    block_x, block_y = ref_band.GetBlockSize()

    # Counters
    d = {"TP" : 0, "TN" : 0, 'FP': 0, 'FN' : 0}

    # Iterate over each raster block
    for y in range(0, ysize, block_y):
        rows = min(block_y, ysize - y)

        for x in range(0, xsize, block_x):
            cols = min(block_x, xsize - x)

            # Data to Array
            ref_arr = ref_band.ReadAsArray(x, y, cols, rows)
            cls_arr = cls_band.ReadAsArray(x, y, cols, rows)

            # Mask
            mask = (
                (ref_arr != ref_nd) &
                (cls_arr != cls_nd)
            )

            ref_valid = ref_arr[mask]
            cls_valid = cls_arr[mask]

            d['TP'] += np.sum((ref_valid == 1) & (cls_valid == 1))
            d['TN'] += np.sum((ref_valid == 0) & (cls_valid == 0))
            d['FP'] += np.sum((ref_valid == 0) & (cls_valid == 1))
            d['FN'] += np.sum((ref_valid == 1) & (cls_valid == 0))
    
    # Get confusion table
    mtx = pd.DataFrame(
        [[d['TP'], d['FP']],
         [d['FN'], d['TN']]],
        columns=['positives', 'negatives'],
        index=['positives', 'negatives']
    )

    # Get evaluation measures
    emeas = calc_confusion_measures(d)

    return mtx, emeas

