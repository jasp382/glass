"""
Image classification
"""

import os
import joblib
import numpy as np

from osgeo import gdal, gdal_array
from joblib import load

from glass.prop.img import rst_epsg
from glass.rd.rst   import rsts_to_featarray, rst_to_refarray
from glass.wt.rst   import obj_to_rst


def img_clustering(imgs, out, method="k-means", n_cls=8):
    """
    Clustering methods implementation

    methods:
    * k-means
    * mean-shift
    """
    
    from sklearn.cluster import MeanShift, KMeans
    from sklearn.cluster import estimate_bandwidth

    from glass.prop.img import rst_epsg
    from glass.pys import obj_to_lst
    
    gdal.UseExceptions()
    gdal.AllRegister()

    imgs = obj_to_lst(imgs)

    arrays, nds = [], []

    ysize, xsize = None, None
    dtype = None

    gtrans, epsg = None, None

    for img in imgs:
        isrc = gdal.Open(img, gdal.GA_ReadOnly)

        if not epsg:
            epsg = rst_epsg(isrc)
        
        if not gtrans:
            gtrans = isrc.GetGeoTransform()

        if not ysize:
            ysize = isrc.RasterYSize
        
        if not xsize:
            xsize = isrc.RasterXSize
        
        if not dtype:
            dtype = gdal_array.GDALTypeCodeToNumericTypeCode(
                isrc.GetRasterBand(1).DataType
            )

        nbnd = isrc.RasterCount

        for b in range(nbnd):
            nds.append(isrc.GetRasterBand(b+1).GetNoDataValue())
            arrays.append(isrc.GetRasterBand(b+1).ReadAsArray())
    
    # Join Arrays
    jarray = np.zeros((ysize, xsize, len(arrays)), dtype)

    for b in range(jarray.shape[2]):
        jarray[:, :, b] = arrays[b]
    
    # Reshape arrays for classification
    if len(arrays) > 1:
        new_shape = (jarray.shape[0] * jarray.shape[1], jarray.shape[2])
        
        X = jarray[:, :, :len(arrays)].reshape(new_shape)
    
    else:
        X = jarray.reshape((-1, 1))

    if method == 'k-means':
        mdl = KMeans(n_clusters=n_cls)
    
    else:
        bandwith = estimate_bandwidth(X, quantile=0.2, n_samples=500)

        mdl = MeanShift(bandwidth=bandwith, bin_seeding=True)
            
    mdl.fit(X)
    
    X_cluster = mdl.labels_
    
    if len(arrays) > 1:
        X_cluster = X_cluster.reshape(jarray[:, :, 0].shape)
    else:
        X_cluster = X_cluster.reshape(jarray.shape)
    
    # Place nodata values
    for r in range(len(arrays)):
        np.place(X_cluster, arrays[r] == nds[r], 255)
    
    return obj_to_rst(X_cluster, out, gtrans, epsg, noData=255)


def train_to_mdl(train_rst, imgs, outmdl, ntrees=1000, fileformat='.tif',
                 method='RandomForest', mxsamples=None, randomtrain=None, sample_dim=100000):
    """
    Train a model for classification and save the model in a file

    Classifiers available:
    * Random Forest;
    * NaiveBayes;
    * LinearSupportVectorMachine;
    * LogisticRegression.

    if randomtrain, Extract random pixels from train file
    """

    from sklearn.ensemble     import RandomForestClassifier
    from sklearn.naive_bayes  import MultinomialNB
    from sklearn.svm          import LinearSVC
    from sklearn.linear_model import LogisticRegression

    mavailable = [
        'RandomForest', 'LinearSupportVectorMachine',
        'LogisticRegression', 'NaiveBayes'
    ]

    method = 'RandomForest' if method not in mavailable \
        else method

    if type(imgs) != list:
        # Check if it is a folder
        if os.path.isdir(imgs):
            # List images in folder
            from glass.pys.oss import lst_ff

            imgs = lst_ff(
                imgs,
                file_format=fileformat if fileformat else '.tif'
            )
        
        else:
            imgs = [imgs]
    
    # Open Data
    num_ref, nd_val, ref_shp = rst_to_refarray(train_rst, rmnd=None)
    
    img_var = [gdal.Open(i, gdal.GA_ReadOnly) for i in imgs]

    # Get band number for each raster
    img_bnd = [i.RasterCount for i in img_var]

    # Check images shape
    # Return error if the shapes are different
    for r in img_var:
        rst_shp = (r.RasterYSize, r.RasterXSize)

        if ref_shp != rst_shp:
            raise ValueError((
                'There are at least two raster '
                'files with different shape'
            ))

    # Get Number of features
    nvar = sum(img_bnd)

    # Get Y - train data without nodata value
    Y = num_ref[num_ref != nd_val]

    # Get X - var data to array, delete nodata and reshape
    X = np.zeros((
        Y.shape[0], nvar),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            img_var[0].GetRasterBand(1).DataType
        )
    )

    f = 0
    for r in range(len(img_var)):
        for b in range(img_bnd[r]):
            a = img_var[r].GetRasterBand(b + 1).ReadAsArray()
            a = a.reshape((-1, 1))
            a = a[num_ref != nd_val]

            X[:, f] = a

            f += 1
    
    # if random train
    if randomtrain and sample_dim:
        # Produce Random Samples for each class in Y
        # Mantain class proportion in random samples
        val = list(np.unique(Y)) # Get Classes
        freq = np.bincount(Y) # Get classes absolute frequencies
        freq = freq[freq != 0]

        # Get classes relative frequencies
        ncells = freq.sum()
        perc = [i / ncells * 100 for i in freq]

        # Get Number of random cells for each class in the random sample
        # The goal is to mantain class proportion in random sample
        ncells_by_class = [int(round(c * sample_dim / 100, 0)) for c in perc]

        # Get Y sub-array for each class
        ny = [Y[Y == v] for v in val]
        # Get indices to use in the training process
        # Select indices randomly
        ry = [np.random.choice(
            np.arange(ny[i].size), size=ncells_by_class[i],
            replace=False
        ) for i in range(len(ncells_by_class))]

        # Place 0 in ny array's... 0 cells will be used for training
        for i in range(len(ry)):
            ny[i][ry[i]] = 0

        # Get X values for ny array's
        nx = [X[Y == v] for v in val]

        # Get Y array's only with cells for training
        # Put there original class ID
        sy = [i[i == 0] for i in ny]
        for i in range(len(sy)):
            sy[i][:] = val[i]
    
        # Select random X cells
        rx = [nx[v][ny[v] == 0] for v in range(len(val))]

        # Put every class array into only one
        # Do it for X and Y
        new_y = sy[0]
        new_x = rx[0]
        for i in range(1, len(sy)):
            new_y = np.concatenate((new_y, sy[i]), axis=0)
            new_x = np.concatenate((new_x, rx[i]), axis=0)
        
        X, Y = new_x, new_y

    # Fit model
    if method == 'RandomForest':
        m = RandomForestClassifier(
            n_estimators=ntrees, random_state=0, n_jobs=-1,
            max_samples=mxsamples
        )
    
    elif method == 'NaiveBayes':
        m = MultinomialNB()
    
    elif method == 'LinearSupportVectorMachine':
        m = LinearSVC()
    
    elif method == 'LogisticRegression':
        m = LogisticRegression(
            n_jobs=1, C=1e5, multi_class='auto',
            solver='lbfgs'
        )
    
    m.fit(X, Y)

    # Save model
    joblib.dump(m, outmdl)

    return outmdl


def imgcls_from_mdl(mdl, imgvar, outrst, fileformat='.tif', newmodel=None, probrst=None):
    """
    Classification from Model File
    """

    if type(imgvar) != list:
        # Check if it is a folder
        if os.path.isdir(imgvar):
            from glass.pys.oss import lst_ff

            imgvar = lst_ff(
                imgvar,
                file_format=fileformat if fileformat else '.tif'
            )
        
        else:
            imgvar = [imgvar]

    # Read model file
    rf = load(mdl)

    # Get Features
    x, nx = rsts_to_featarray(imgvar)

    # Predict
    y_cls = rf.predict(nx)

    # Reshape result
    res = y_cls.reshape(x[:, :, 0].shape)

    # Open Ref image
    refi = gdal.Open(imgvar[0], gdal.GA_ReadOnly)

    # Get NoData Value
    nd_val = refi.GetRasterBand(1).GetNoDataValue()
    
    # Get transform
    gtrans = refi.GetGeoTransform()

    # Get SRS
    srs = rst_epsg(refi)

    # Place nodata values
    tmp = refi.GetRasterBand(1).ReadAsArray()
    np.place(res, tmp==nd_val, 255)

    # Export result
    obj_to_rst(res, outrst, gtrans, srs, noData=255)

    if newmodel:
        joblib.dump(rf, newmodel)
    
    # Process probability rasters
    if probrst:
        _classes = rf.classes_

        proba = rf.predict_proba(nx)

        probs = [proba[:, i] for i in range(proba.shape[1])]

        # Reshape
        _res = [a.reshape(x[:, :, 0].shape) for a in probs]

        # Place NoData Value and export
        for i in range(len(_res)):
            np.place(_res[i], tmp==nd_val, 2)

            obj_to_rst(
                _res[i],
                os.path.join(probrst, f'prob_{str(_classes[i])}.tif'),
                gtrans, srs, noData=2
            )
    

    return outrst, None #rf.feature_importances_



def bincls_basedonprob(mdl, feat, prob_range, mixcls, orst, fileformat='.tif'):
    """
    Binary classication

    Probabilities between an certain range
    will be considered mixed pixels
    """

    from glass.pys.oss import fprop

    outf = os.path.dirname(orst)
    fname = fprop(orst, 'fn')

    if type(feat) != list:
        # Check if it is a folder
        if os.path.isdir(feat):
            from glass.pys.oss import lst_ff

            feat = lst_ff(
                feat,
                file_format=fileformat if fileformat else '.tif'
            )
        
        else:
            feat = [feat]
    
    # Get probability range
    minprob, maxprob = prob_range
    
    # Load Model
    mdl_data = load(mdl)

    # Get features
    x, cx = rsts_to_featarray(feat)

    # Predict and get probabilities
    ycls  = mdl_data.predict(cx)
    proba = mdl_data.predict_proba(cx)
    prob  = proba[:, 0]

    # Reshape
    clsres  = ycls.reshape(x[:, :, 0].shape)
    probres = prob.reshape(x[:, :, 0].shape)

    # Compute final result
    fcls = np.where(
        (probres >= minprob) & (probres <= maxprob),
        mixcls, clsres
    )

    # Export results
    # Open Ref image
    refi = gdal.Open(feat[0], gdal.GA_ReadOnly)

    # Get NoData Value
    nd_val = refi.GetRasterBand(1).GetNoDataValue()
    
    # Get transform
    gtrans = refi.GetGeoTransform()

    # Get SRS
    srs = rst_epsg(refi)

    # Place nodata values
    tmp = refi.GetRasterBand(1).ReadAsArray()
    np.place(fcls, tmp==nd_val, 255)
    np.place(probres, tmp==nd_val, 255)
    np.place(clsres, tmp==nd_val, 255)

    # Create new files
    obj_to_rst(fcls, orst, gtrans, srs, noData=255)
    ocls = obj_to_rst(
        clsres,
        os.path.join(outf, f'{fname}_ocls.tif'),
        gtrans, srs, noData=255
    )

    oprob = obj_to_rst(
        probres,
        os.path.join(outf, f'{fname}_prob.tif'),
        gtrans, srs, noData=255
    )

    return orst

