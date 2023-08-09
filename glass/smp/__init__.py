"""
Tools for sampling
"""


"""
Get values for sample from raster
"""

def pnt_val_on_rst(pntX, pntY, raster, geotransform=None,
                               rstShape=None):
    """
    Extract, for a given point, the value of a cell with the same location
    """
    
    import os
    import numpy
    from osgeo import gdal
    
    if type(raster) == str:
        if os.path.isfile(raster):
            img = gdal.Open(raster)
            geo_transform = img.GetGeoTransform()
            band = img.GetRasterBand(1)
        
            if not rstShape:
                tmpArray = numpy.array(band.ReadAsArray())
                nrLnh, nrCols = tmpArray.shape
        
            else:
                nrLnh, nrCols = rstShape
        
        else:
            raise ValueError('Raster is a string but not a file')
    
    else:
        geo_transform = geotransform if geotransform else None
        if not geo_transform:
            raise ValueError(
                'If raster is not a file, geotransform must be specified')
        
        if not rstShape:
            tmpArray = numpy.array(raster.ReadAsArray())
            nrLnh, nrCols = tmpArray.shape
        
        else:
            nrLnh, nrCols = rstShape
        
        band = raster
    
    px = int((pntX - geo_transform[0]) / geo_transform[1])
    py = int((pntY - geo_transform[3]) / geo_transform[5])
    
    if px < 0 or px > nrCols:
        return 0
    
    if py < 0 or py > nrLnh:
        return 0
    
    cell_value = band.ReadAsArray(px, py, 1, 1)
    
    cell_value = float(cell_value) if cell_value else None
    
    return cell_value


def gdal_valuesList_to_pointsList(raster, points_xy):
    import numpy
    from osgeo import gdal
    
    img = gdal.Open(raster)
    
    geo_transform = img.GetGeoTransform()
    band = img.GetRasterBand(1)
    
    array = numpy.array(band.ReadAsArray())
    lnh, col = array.shape
    
    values = []
    for pnt in points_xy:
        px = int((pnt[0] - geo_transform[0]) / geo_transform[1])
        
        if px < 0 or px > col:
            values.append(-9999)
            continue
        
        py = int((pnt[1] - geo_transform[3]) / geo_transform[5])
        if py < 0 or py > lnh:
            values.append(-9999)
            continue
        
        val = band.ReadAsArray(px, py, 1, 1)
        
        values.append(float(val))
    
    return values


def rst_val_to_points(pnt, rst):
    """
    Extract, for a given point dataset, the value of a cell with the same location
    
    Returns a dict:
    
    d = {
        fid: value,
        ...
    }
    """
    
    from osgeo         import ogr, gdal
    from glass.prop.df import drv_name
    
    values_by_point = {}
    shp = ogr.GetDriverByName(drv_name(pnt)).Open(pnt, 0)
    lyr = shp.GetLayer()
    
    img = gdal.Open(rst)
    geo_transform = img.GetGeoTransform()
    band = img.GetRasterBand(1)
    
    for feat in lyr:
        geom = feat.GetGeometryRef()
        mx, my = geom.GetX(), geom.GetY()
        px = int((mx - geo_transform[0]) / geo_transform[1])
        py = int((my - geo_transform[3]) / geo_transform[5])
        
        val_pix = band.ReadAsArray(px, py, 1, 1)
        
        values_by_point[int(feat.GetFID())] = float(val_pix[0][0])
    
    return values_by_point


def rst_val_to_points2(pntShp, listRasters):
    """
    Pick raster value for each point in pntShp
    """
    
    from osgeo         import ogr, gdal
    from glass.pys     import obj_to_lst
    from glass.prop.df import drv_name
    
    listRasters = obj_to_lst(listRasters)
    
    shp = ogr.GetDriverByName(
        drv_name(pntShp)).Open(pnt, 0)
    
    lyr = shp.GetLayer()
    
    pntDict = {}
    for feat in lyr:
        geom = feat.GetGeometryRef()
        
        x, y = geom.GetX(), geom.GetY()
        
        l = []
        for rst in listRasters:
            img = gdal.Open(rst)
            geo_transform = img.GetGeoTransform()
            band = img.GetRasterBand(1)
            
            px = int((x - geo_transform[0]) / geo_transform[1])
            py = int((y - geo_transform[3]) / geo_transform[5])
            value = band.ReadAsArray(px, py, 1, 1)
            
            l.append(list(value)[0])
            
            del img, geo_transform, band, px, py
        
        pntDict[feat.GetFID()] = l
    
    shp.Destroy()
    
    return pntDict


"""
Extract features from files
"""

def extract_random_features(inshp, nfeat, outshp, is_percentage=None):
    """
    Extract Random features from one Feature Class
    and save them in a new file
    """

    import numpy as np
    from glass.rd.shp   import shp_to_obj
    from glass.wt.shp   import obj_to_shp
    from glass.prop.prj import shp_epsg

    # Open data
    df = shp_to_obj(inshp)

    # Get number of random features
    n = int(round(nfeat * df.shape[0] / 100, 0)) if is_percentage else nfeat

    # Get random sample
    df['idx'] = df.index
    rnd = np.random.choice(df.idx, n, replace=False)

    # Filter features
    rnd_df = df[df.idx.isin(rnd)]

    rnd_df.drop('idx', axis=1, inplace=True)

    # Save result
    epsg = shp_epsg(inshp)
    return obj_to_shp(rnd_df, 'geometry', epsg, outshp)


"""
Extract Cells from Raster
"""

def proprndcells_to_rst(inrst, class_proportion, out_rst,
    sample_dim, cls_sample_min=None):
    """
    Extract some cells from one raster and save them into a new raster

    The cells are extracted in a random way for each class in inrst.
    The number of cells extracted for each class are based on the values
    in class_proportion object
    """

    from osgeo        import gdal
    import numpy      as np
    from glass.prop.img import rst_epsg
    from glass.wt.rst   import obj_to_rst

    img = gdal.Open(inrst, gdal.GA_ReadOnly)

    nd_val = img.GetRasterBand(1).GetNoDataValue()

    # Image to array
    num_ref = img.GetRasterBand(1).ReadAsArray()

    # Reshape array
    oned_ref = num_ref.reshape(num_ref.shape[0] * num_ref.shape[1])

    # Get classes in inrst array
    id_cls = list(np.unique(oned_ref))

    # Remove nodata value from id_cls
    if nd_val in id_cls:
        id_cls.remove(nd_val)
    
    # All classes in class_proportion must be in id_cls
    ks = list(class_proportion.keys())
    for k in ks:
        if k not in id_cls:
            del class_proportion[k]

    # Exclude values not in ks
    ks = list(class_proportion.keys())
    __id_cls = id_cls.copy()
    for c in __id_cls:
        if c not in ks:
            id_cls.remove(c)
    
    # Get absolute frequencies of inrst
    # Exclude no data values
    ref_sem_nd = oned_ref[oned_ref != nd_val]
    freq = np.bincount(ref_sem_nd)
    freq = freq[freq != 0]

    # Get number of cells for each class based on class_proportions
    class_cells = {c : int(round(
        class_proportion[c] * sample_dim /100, 0
    )) for c in class_proportion}

    # The n_cells for each class could not be lesser than
    # cls_sample_min
    for c in class_cells:
        if cls_sample_min:
            if class_cells[c] < cls_sample_min:
                class_cells[c] = cls_sample_min
        
        # n_cells for each class could not be larger than the class frequency
        for e in range(len(id_cls)):
            if id_cls[e] == c:
                if freq[e] < class_cells[c]:
                    class_cells[c] = freq[e]
                
                break
    
    # Get index array
    idx_ref = np.arange(oned_ref.size)

    # Get indexes for cells of each class
    idx_cls = [idx_ref[oned_ref == c] for c in id_cls]

    # Get indexes to be selected for each class
    sel_cls = [np.random.choice(
        idx_cls[e], size=class_cells[id_cls[e]],
        replace=False
    ) for e in range(len(id_cls))]

    # Create result
    res = np.zeros(oned_ref.shape, dtype=oned_ref.dtype)

    # Place selected cells in result array
    for c in range(len(id_cls)):
        res[sel_cls[c]] = id_cls[c]
    
    # Place nodata
    np.place(res, oned_ref == nd_val, nd_val)
    np.place(res, res == 0, nd_val)

    # Reshape
    res = res.reshape(num_ref.shape)

    # Save result
    obj_to_rst(res, out_rst, img.GetGeoTransform(), rst_epsg(img), noData=nd_val)

    return out_rst
