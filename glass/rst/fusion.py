"""
Data Fusion Tools
"""


def pca(bands, ofolder, oname):
    """
    Run Principal Component Analysis

    refs:
    https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60
    https://towardsdatascience.com/a-step-by-step-explanation-of-principal-component-analysis-b836fb9c97e2
    """

    import os
    import numpy as np
    from osgeo import gdal, gdal_array
    from sklearn.decomposition import PCA

    from glass.wt.rst import obj_to_rst

    # Open Images
    img_src = [gdal.Open(i, gdal.GA_ReadOnly) for i in bands]

    ndVal = img_src[0].GetRasterBand(1).GetNoDataValue()

    img_x = np.zeros((
        img_src[0].RasterYSize, img_src[0].RasterXSize, len(img_src)),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            img_src[0].GetRasterBand(1).DataType
        )
    )

    for b in range(img_x.shape[2]):
        img_x[:, :, b] = img_src[b].GetRasterBand(1).ReadAsArray()
    
    # Reshape Array
    new_shape = (img_x.shape[0] * img_x.shape[1], img_x.shape[2])
    X = img_x[:, :, :8].reshape(new_shape)

    # Run PCA
    pca = PCA(n_components=X.shape[1])

    X_pca = pca.fit_transform(X)

    # Reshape PCA results
    X_pca = X_pca.reshape(img_x[:, :, :].shape)

    pca_array = [np.zeros((X_pca.shape[0], X_pca.shape[1]), X_pca.dtype) for i in range(X_pca.shape[2])]

    for i in range(X_pca.shape[2]):
        pca_array[i][:, :] = X_pca[:, :, i]
    
    # Save results
    tmp = img_src[0].GetRasterBand(1).ReadAsArray()

    for i in range(len(pca_array)):
        nd_nd = np.amin(pca_array[i]) - 1

        np.place(pca_array[i], tmp==ndVal, nd_nd)

        obj_to_rst(
            pca_array[i],
            os.path.join(ofolder, f'{oname}_c{str(i+1)}.tif'),
            bands[0], noData=nd_nd
        )

    return ofolder

