"""
Measure separability
"""

import numpy as np
import pandas as pd

from osgeo import gdal, gdal_array



def r_separability(trainref, trainvar, omtx):
    """
    Use R Statistics to calculate separability between classes

    Info about separability tool

    https://www.rdocumentation.org/packages/spatialEco/versions/1.3-0/topics/separability
    """

    import os

    import rpy2.robjects as robjects
    from rpy2.robjects import numpy2ri
    from rpy2.robjects.packages import importr

    from glass.wt import obj_to_tbl

    # Import R package
    sp = importr('spatialEco')

    # Enable conversion between numpy and R objects
    numpy2ri.activate()

    separability = robjects.r['separability']

    # Open data
    img_ref = gdal.Open(trainref, gdal.GA_ReadOnly)
    img_var = [gdal.Open(i, gdal.GA_ReadOnly) for i in trainvar]

    # Data To Array
    num_ref = img_ref.GetRasterBand(1).ReadAsArray()
    num_ref = num_ref.reshape((-1, 1))
    img_num = [x.GetRasterBand(1).ReadAsArray() for x in img_var]
    img_num = [x.reshape((-1, 1)) for x in img_num]

    # Get Classes codes
    nd_val = img_ref.GetRasterBand(1).GetNoDataValue()

    classes = np.unique(num_ref)
    classes = classes[classes != nd_val]

    # Create samples for each class
    cls_samples = {}
    for cls in classes:
        for v in range(len(img_num)):
            if not v:
                cls_samples[cls] = [img_num[v][num_ref == cls]]
            else:
                cls_samples[cls].append(img_num[v][num_ref == cls])

    # Get separability matrix - one for each variable samples
    mtxs = []
    for v in range(len(img_num)):
        mtx = []
        for i in range(classes.shape[0]):
            row = []
            for e in range(classes.shape[0]):
                if i < e:
                    sep_val = None
                else:
                    b, jm, m, mdif, d, td = separability(
                        cls_samples[classes[i]][v],
                        cls_samples[classes[e]][v]
                    )[0]
            
                    sep_val = td
        
                row.append(sep_val)
            mtx.append(row)
        mtxs.append(pd.DataFrame(mtx, index=classes, columns=classes))

    for df in range(len(mtxs)):
        mtxs[df]['classe'] = mtxs[df].index
    
    # Export result
    obj_to_tbl(mtxs, omtx, sheetsName=[
        os.path.basename(f) for f in trainvar
    ])

    return omtx


def bhattacharyya_distance(mean1, cov1, mean2, cov2):
    dist = 0.125 * (mean2 - mean1).T @ np.linalg.inv(0.5 * (cov1 + cov2)) @ (mean2 - mean1)
    return dist


def separability_matrix(refrst, featfolder, classes_leg, out_tbl, fformat='.tif'):
    """
    Compute separability matrices
    * Bhattacharyya Distance
    * Jeffries-Matusita Distance

    Inputs:
    * refrst - raster with LULC classes
    * featfolder - path to folder where the features
    are stored
    * classes_leg - relation between class ID and class label
    * out_tbl - path to the output table
    """

    import math as m
    from glass.pys.oss import lst_ff
    from glass.wt import obj_to_tbl

    # List feature files
    featfiles = lst_ff(featfolder, file_format=fformat)

    # Open Data
    refimg = gdal.Open(refrst, gdal.GA_ReadOnly)
    feats = [gdal.Open(i, gdal.GA_ReadOnly) for i in featfiles]

    # Get Ref NoData Value
    ndval = refimg.GetRasterBand(1).GetNoDataValue()

    # Get band number for each raster
    featbands = [i.RasterCount for i in feats]

    # Get number of features
    nfeat = sum(featbands)

    # Convert imgs to Array, remove nodata values and reshape
    refnum = refimg.GetRasterBand(1).ReadAsArray()
    refnum = refnum.reshape((-1, 1))

    # Get Ref array without nodata value
    refref = refnum[refnum != ndval]

    # Get features array
    featnum = np.zeros((
        refref.shape[0], nfeat),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            feats[0].GetRasterBand(1).DataType
        )
    )

    f = 0
    for r in range(len(feats)):
        for b in range(featbands[r]):
            a = feats[r].GetRasterBand(b+1).ReadAsArray()
            a = a.reshape((-1, 1))
            a = a[refnum != ndval]

            featnum[:, f] = a

            f += 1
    
    # ID classes
    classes = np.unique(refref)

    # Create an array with the distribuitions
    # for each class
    clsdist = []
    for cls in classes:
        clsdist.append(featnum[refref == cls])
    
    # Get Mean and Covariance matrix
    means, covs = [], []

    for sa in clsdist:
        means.append(np.mean(sa, axis=0))
        covs.append(np.cov(sa.T))
    
    # Compute Bhattacharyya distance
    # for each pair of classes
    ftbl_bd, ftbl_jf = [], []
    for c in range(len(classes)):
        _bd = [classes_leg[classes[c]]]
        _jf = [classes_leg[classes[c]]]
    
        for _c in range(len(classes)):
            # Compute Bhattacharyya distance between two distributions
            bdistance = bhattacharyya_distance(
                means[c], covs[c],
                means[_c], covs[_c]
            )

            # Compute Jeffries-Matusita distance
            jeffries = 2 * (1 - m.exp(-bdistance))

            _bd.append(bdistance)
            _jf.append(jeffries)

        ftbl_bd.append(_bd)
        ftbl_jf.append(_jf)
    
    # Generate final table
    cols = ['class'] + [classes_leg[c] for c in classes]
    df_bd = pd.DataFrame(ftbl_bd, columns=cols)
    df_jf = pd.DataFrame(ftbl_jf, columns=cols)

    obj_to_tbl([df_bd, df_jf], out_tbl, sheetsName=[
        'Bhattacharyya', 'Jeffries'
    ])

    return out_tbl

