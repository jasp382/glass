"""
Measure separability
"""

import numpy as np
from math import exp, sqrt, log


def bha_dist(cls_a, cls_b):
    """
    Return Bhattacharyya distance
    """

    # Get mean's array
    mean_a = np.mean(cls_a, axis=0)
    mean_b = np.mean(cls_b, axis=0)
    
    # Get covariance matrix
    cov_a = np.cov(cls_a, rowvar=False)
    cov_b = np.cov(cls_b, rowvar=False)
    
    # Diference mean vector
    dm = (mean_a - mean_b)
    
    s12 = (cov_a + cov_b) / 2
    
    # Singular covariance matrix
    invmatr = np.linalg.inv((cov_a + cov_b) / 2)
    
    # Mahalanobis distance (MH):
    tmp = np.dot(dm.T, invmatr)
    tmp = np.dot(tmp, dm)
    MH = sqrt(tmp)
    
    # Bhattacharyya distance (B):
    tmp = np.linalg.det(s12) / sqrt( np.linalg.det(cov_a)*np.linalg.det(cov_b) )
    tmp = log(tmp)
    B = MH/8.0 + tmp/2.0
    
    return B


def jm_dist(ba):
    # J-M distance:
    JM = sqrt(2 * (1 - exp(-ba)))
    
    return JM

def td(cls_a, cls_b):
    """
    Return Transformed divergence
    """
    
    # Get mean's array
    mean_a = np.matrix(np.mean(cls_a, axis=0))
    mean_b = np.matrix(np.mean(cls_b, axis=0))
    
    # Get covariance matrix
    cov_a = np.matrix(np.cov(cls_a, rowvar=False))
    cov_b = np.matrix(np.cov(cls_b, rowvar=False))
    
    # Term 1
    term1 = 0.5 * np.trace(np.dot(
        cov_a - cov_b,
        np.linalg.inv(cov_b) - np.linalg.inv(cov_a)
    ))
    
    # Term 2
    dm = np.matrix(mean_a - mean_b).T
    
    fprod = np.linalg.inv(cov_a) + np.linalg.inv(cov_b)
    
    term2 = 0.5 * np.trace(
        np.dot(np.dot(fprod, dm), dm.T)
    )
    
    # Divergence
    d = term1 + term2
    
    # Transformed divergence
    _td = 2 * (1 - exp(-(d/8.0)))
    
    return _td


def clsep_matrix(ref, var, out, fileformat=None):
    """
    Produce matrix with classes separability from a satelite
    images
    """

    import os
    
    import pandas    as pd
    from osgeo       import gdal, gdal_array
    from glass.wt import obj_to_tbl

    # Open data
    ref_src = gdal.Open(ref, gdal.GA_ReadOnly)

    if type(var) != list:
        # Check if it is a folder
        if os.path.isdir(var):
            # List images in folder
            from glass.pys.oss import lst_ff

            var = lst_ff(
                var,
                file_format=fileformat if fileformat else '.tif'
            )
        
        else:
            var = [var]
    
    var_src = [gdal.Open(i, gdal.GA_ReadOnly) for i in var]

    # Get Band number for each raster
    img_bnd = [i.RasterCount for i in var_src]

    # Check images shape
    # Return error if the shapes are different
    ref_shp = (ref_src.RasterYSize, ref_src.RasterXSize)
    for r in var_src:
        rst_shp = (r.RasterYSize, r.RasterXSize)

        if ref_shp != rst_shp:
            raise ValueError(
                'There are at least two raster files with different shape'
            )
    
    # Get NoData Value
    nd_val = ref_src.GetRasterBand(1).GetNoDataValue()

    # Get Number of features
    nvar = sum(img_bnd)

    # Convert imgs to Array, remove nodata values and reshape
    ref_num = ref_src.GetRasterBand(1).ReadAsArray()
    ref_num = ref_num.reshape((-1, 1))

    ref_num_ = ref_num[ref_num != nd_val]

    X = np.zeros(
        (ref_num_.shape[0], nvar),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            var_src[0].GetRasterBand(1).DataType
        )
    )

    f = 0
    for r in range(len(var_src)):
        for b in range(img_bnd[r]):
            a = var_src[r].GetRasterBand(b + 1).ReadAsArray()
            a = a.reshape((-1, 1))
            a = a[ref_num != nd_val]

            X[:, f] = a

            f += 1
    
    # Create arrays for each class
    classes = list(np.sort(np.unique(ref_num_)))

    clsdata = [X[ref_num_ == c] for c in classes]

    # Get separability matrix
    mtx_b  = []
    mtx_jm = []

    for v in range(len(classes)):
        row_b = []
        row_jm = []
        for v_ in range(len(classes)):
            if v < v_:
                b  = None
                jm = None
            else:
                b = bha_dist(
                    clsdata[v], clsdata[v_]
                )

                jm = jm_dist(b)
            
            row_b.append(b)
            row_jm.append(jm)
        
        mtx_b.append(row_b)
        mtx_jm.append(row_jm)
    
    mtx_bd = pd.DataFrame(mtx_b, columns=classes, index=classes)
    mtx_bd.reset_index(inplace=True)
    mtx_bd.rename(columns={'index' : 'class_id'}, inplace=True)

    mtx_jm = pd.DataFrame(mtx_jm, columns=classes, index=classes)
    mtx_jm.reset_index(inplace=True)
    mtx_jm.rename(columns={'index' : 'class_id'}, inplace=True)

    obj_to_tbl([mtx_bd, mtx_jm], out, sheetsName=['Bhattacharyya_Distance', 'Jeffries-Matusita'])

    return out
