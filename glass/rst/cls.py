"""
Image classification
"""

def k_means(imgFiles, out, n_cls=8):
    """
    K-Means implementation
    """
    
    import os
    from osgeo          import gdal, gdal_array
    import numpy        as np
    from sklearn        import cluster
    from glass.wt.rst import obj_to_rst
    
    gdal.UseExceptions()
    gdal.AllRegister()
    
    singleBand = None
    if type(imgFiles) != list:
        # Check if img is a valid file
        if not os.path.exists(imgFiles):
            raise ValueError("{} is not a valid file".format(imgFiles))
        
        img_src = gdal.Open(imgFiles, gdal.GA_ReadOnly)
        
        n_bnd = img_src.RasterCount
        
        ndVal = img_src.GetRasterBand(1).GetNoDataValue()
        
        if n_bnd == 1:
            band = img_src.GetRasterBand(1)
            
            img = band.ReadAsArray()
            
            singleBand = 1
            #X = img.reshape((-1, 1))
        
        else:
            img = np.zeros(
                (img_src.RasterYSize, img_src.RasterXSize, n_bnd),
                gdal_array.GDALTypeCodeToNumericTypeCode(
                    img_src.GetRasterBand(1).DataType
                )
            )
            
            for b in range(img.shape[2]):
                img[:, :, b] = img_src.GetRasterBand(b + 1).ReadAsArray()
    
    else:
        img_src = [gdal.Open(i, gdal.GA_ReadOnly) for i in imgFiles]
        
        ndVal = img_src[0].GetRasterBand(1).GetNoDataValue()
        
        n_bnd = len(img_src)
        
        img = np.zeros((
            img_src[0].RasterYSize, img_src[0].RasterXSize, len(img_src)),
            gdal_array.GDALTypeCodeToNumericTypeCode(
                img_src[0].GetRasterBand(1).DataType
            )
        )
        
        for b in range(img.shape[2]):
            img[:, :, b] = img_src[b].GetRasterBand(1).ReadAsArray()
    
    # Reshape arrays for classification
    if not singleBand:
        new_shape = (img.shape[0] * img.shape[1], img.shape[2])
        
        X = img[:, :, :n_bnd].reshape(new_shape)
    
    else:
        X = img.reshape((-1, 1))
            
    kmeans = cluster.KMeans(n_clusters=n_cls)
            
    kmeans.fit(X)
    
    X_cluster = kmeans.labels_
    
    if not singleBand:
        X_cluster = X_cluster.reshape(img[:, :, 0].shape)
    else:
        X_cluster = X_cluster.reshape(img.shape)
    
    # Place nodata values
    if type(imgFiles) != list:
        tmp = img_src.GetRasterBand(1).ReadAsArray()
    else:
        tmp = img_src[0].GetRasterBand(1).ReadAsArray()
    
    np.place(X_cluster, tmp==ndVal, 255)
    
    return obj_to_rst(
        X_cluster, out,
        imgFiles if type(imgFiles) != list else imgFiles[0],
        noData=255
    )


def train_to_mdl(train_rst, imgs, outmdl, ntrees=1000, fileformat='.tif'):
    """
    Train a model for classification and save the model in a file

    Classifiers available:
    * Random Forest;
    """

    import joblib
    import numpy as np
    import os
    from osgeo import gdal, gdal_array
    from sklearn.ensemble import RandomForestClassifier

    # Open Data
    img_ref = gdal.Open(train_rst, gdal.GA_ReadOnly)

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
    
    img_var = [gdal.Open(i, gdal.GA_ReadOnly) for i in imgs]

    # Get band number for each raster
    img_bnd = [i.RasterCount for i in img_var]

    # Check images shape
    # Return error if the shapes are different
    ref_shp = (img_ref.RasterYSize, img_ref.RasterXSize)
    for r in img_var:
        rst_shp = (r.RasterYSize, r.RasterXSize)

        if ref_shp != rst_shp:
            raise ValueError(
                'There are at least two raster files with different shape'
            )

    # Get NoData Value
    nd_val = img_ref.GetRasterBand(1).GetNoDataValue()

    # Get Number of features
    nvar = sum(img_bnd)

    # Convert imgs to Array, remove nodata values and reshape
    num_ref = img_ref.GetRasterBand(1).ReadAsArray()
    num_ref = num_ref.reshape((-1, 1))

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

    # Fit model
    m = RandomForestClassifier(
        n_estimators=ntrees, random_state=0, n_jobs=-1
    )

    m.fit(X, Y)

    # Save model
    joblib.dump(m, outmdl)

    return outmdl


def random_train_to_mdl(train_rst, imgs, outmdl, sample_dim=500000, ntrees=1000):
    """
    Extract random features from train file and save
    them into a Model File

    Works for random forest
    """

    import joblib
    import numpy as np
    from osgeo import gdal, gdal_array
    from sklearn.ensemble import RandomForestClassifier

    # Open Data
    img_ref = gdal.Open(train_rst, gdal.GA_ReadOnly)
    img_var = [gdal.Open(i, gdal.GA_ReadOnly) for i in imgs]

    # Get NoData value
    nd_val = img_ref.GetRasterBand(1).GetNoDataValue()

    # Get Number of features
    nvar = len(img_var)

    # Convert imgs to Array, remove nodata values and reshape
    num_ref = img_ref.GetRasterBand(1).ReadAsArray()
    num_ref = num_ref.reshape((-1, 1))

    # Get Y - reference data without nodata value
    Y = num_ref[num_ref != nd_val]

    # Get X main array
    X = np.zeros(
        (Y.shape[0], nvar),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            img_var[0].GetRasterBand(1).DataType
        )
    )

    # Put feature values as columns in X
    for b in range(X.shape[1]):
        a = img_var[b].GetRasterBand(1).ReadAsArray()
        a = a.reshape((-1, 1))
        a = a[num_ref != nd_val]

        X[:, b] = a
    
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
    
    # Fit model
    clf = RandomForestClassifier(
        n_estimators=ntrees, random_state=0, n_jobs=-1
    )

    clf.fit(new_x, new_y)

    # Save model file
    joblib.dump(clf, outmdl)

    return outmdl


def imgcls_from_mdl(mdl, imgvar, outrst, fileformat='.tif'):
    """
    Classification from Model File
    """

    import os
    from joblib import load
    from osgeo import gdal, gdal_array
    import numpy as np
    from glass.wt.rst import obj_to_rst

    if type(imgvar) != list:
        # Check if it is a folder
        if os.path.isdir(imgvar):
            from glass.pys.oss import lst_ff

            imgvar = lst_ff(
                imgvar, file_format=fileformat if fileformat else '.tif'
            )
        
        else:
            imgvar = [imgvar]

    # Read model file
    rf = load(mdl)

    # Open feature images
    img_var = [gdal.Open(i, gdal.GA_ReadOnly) for i in imgvar]

    # Get NoData Value
    nd_val = img_var[0].GetRasterBand(1).GetNoDataValue()

    # Get band number of each raster
    img_bnd = [i.RasterCount for i in img_var]

    # Check images shape
    ref_shp = (img_var[0].RasterYSize, img_var[0].RasterXSize)
    if len(img_var) > 1:
        for r in range(1, len(img_var)):
            rst_shp = (img_var[r].RasterYSize, img_var[r].RasterXSize)

            if ref_shp != rst_shp:
                raise ValueError(
                    'There are at least two raster files with different shape'
                )

    # Get features number
    nvar = sum(img_bnd)

    # Convert feature images to array
    X = np.zeros(
        (ref_shp[0], ref_shp[1], nvar),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            img_var[0].GetRasterBand(1).DataType
        )
    )

    f = 0
    for r in range(len(img_var)):
        for b in range(img_bnd[r]):
            X[:, :, f] = img_var[r].GetRasterBand(b + 1).ReadAsArray()

            f += 1
    
    # Reshape
    nshp = (X.shape[0] * X.shape[1], X.shape[2])
    n_x = X[:, :, :nvar].reshape(nshp)

    # Predict
    y_cls = rf.predict(n_x)

    # Reshape result
    res = y_cls.reshape(X[:, :, 0].shape)

    # Place nodata values
    tmp = img_var[0].GetRasterBand(1).ReadAsArray()
    np.place(res, tmp==nd_val, 255)

    # Export result
    obj_to_rst(res, outrst, imgvar[0], noData=255)

    return outrst

