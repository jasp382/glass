"""
Image classification
"""

def k_means(imgFiles, out, n_cls=8):
    """
    K-Means implementation
    """
    
    import os
    from osgeo         import gdal, gdal_array
    import numpy       as np
    from sklearn       import cluster
    from glass.geo.gt.torst import obj_to_rst
    
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

