"""
Measure separability
"""

def r_separability(trainref, trainvar, omtx):
    """
    Use R Statistics to calculate separability between classes

    Info about separability tool

    https://www.rdocumentation.org/packages/spatialEco/versions/1.3-0/topics/separability
    """

    import os
    import numpy as np
    import pandas as pd

    from osgeo import gdal

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

