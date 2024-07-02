"""
Image/Raster classification
"""

import os
import joblib
import arcpy
import numpy as np

from glass.pys.oss import lst_ff


def train_to_mdl(trst, feat_folder, outmdl, ntrees=1000, mxsamples=None):
    """
    Train a model for classification and save the model in a file

    Classifiers available:
    * Random Forest;

    if randomtrain, Extract random pixels from train file
    """

    from sklearn.ensemble     import RandomForestClassifier

    from glass.esri.rd.rst import ag_rst_to_refarray, rst_to_array
    from glass.esri.prop.rst import get_nodata

    # List feature rasters
    feats = lst_ff(feat_folder, file_format='.tif')

    # Open data
    refnum, refnd, refshp = ag_rst_to_refarray(trst, rmnd=None)

    fnums = [rst_to_array(r) for r in feats]

    # Get NoData Values
    nds = [get_nodata(r) for r in feats]

    # Check shapes
    for i in range(len(fnums)):
        if refshp != fnums[i].shape:
            raise ValueError((
                f'The file {feats[i]} has a '
                'different shape than the reference raster'
            ))
    
    # Get Y - train data without nodata value
    for i in range(len(nds)):
        np.place(refnum, fnums[i] == nds[i], refnd)
    
    Y = refnum[refnum != refnd]

    # Get X - var data to array, delete nodata and reshape
    X = np.zeros(
        (Y.shape[0], len(fnums)),
        np.float32
    )

    for i in range(len(fnums)):
        fnums[i] = fnums[i].reshape((-1, 1))
        fnums[i] = fnums[i][refnum != refnd]

        X[:, i] = fnums[i]
    
    # Create Model Instance
    m = RandomForestClassifier(
        n_estimators=ntrees, random_state=0,
        n_jobs=-1, max_samples=mxsamples
    )

    # Model fit
    m.fit(X, Y)

    # Save model
    joblib.dump(m, outmdl)

    return outmdl


def imgcls_from_mdl(mdl, featfolder, orst, probrst=None):
    """
    Classification from Model File
    """

    from glass.esri.rd.rst import rst_to_array
    from glass.esri.prop.rst import rst_geoprop, get_nodata
    from glass.esri.wt import obj_to_rst

    # List feature rasters
    feats = lst_ff(featfolder, file_format='.tif')

    # Read model file
    rf = joblib.load(mdl)

    # Get feature data
    fnums = [rst_to_array(r) for r in feats]

    # Get NoData Values
    nds = [get_nodata(r) for r in feats]

    # Verify rasters shape
    refshp = fnums[0].shape

    for i in range(1, len(fnums)):
        np.place(fnums[i], fnums[i] == nds[i], -9999)
        if refshp != fnums[i].shape:
            raise ValueError((
                f'The file {feats[i]} has a '
                'different shape than the first feature raster'
            ))
        
    # Get X - array with all features data
    X = np.zeros(
        (refshp[0], refshp[1], len(fnums)),
        np.float32
    )

    for i in range(len(fnums)):
        X[:, :, i] = fnums[i]

    # Reshape
    nshp = (X.shape[0] * X.shape[1], X.shape[2])
    n_x = X[:, :, :len(fnums)].reshape(nshp)

    # Predict
    y_cls = rf.predict(n_x)

    # Reshape result
    res = y_cls.reshape(X[:, :, 0].shape)

    # Get geo properties
    lwleft, csize = rst_geoprop(feats[0])

    # Place nodata values
    for i in range(len(feats)):
        np.place(res, fnums[i] == -9999, 255)
    
    # Export result
    obj_to_rst(res, orst, lwleft, csize, 255)

    # Process probability rasters
    rst_probs = []
    if probrst:
        _classes = rf.classes_

        proba = rf.predict_proba(n_x)

        probs = [proba[:, i] for i in range(proba.shape[1])]

        # Reshape
        _res = [a.reshape(X[:, :, 0].shape) for a in probs]

        # Place NoData Value and export
        for i in range(len(_res)):
            for r in range(len(feats)):
                np.place(_res[i], fnums[r] == nds[r], 2)

            op = obj_to_rst(
                _res[i],
                os.path.join(probrst, f'prob_{str(_classes[i])}.tif'),
                lwleft, csize, 2
            )

            rst_probs.append(op)
    
    return orst, rst_probs

