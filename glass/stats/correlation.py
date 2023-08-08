"""
Execute statistic analysis using GDAL Library
"""


def pearson_correlation(x, y):
    """
    Pearson correlation between two raster images
    
    The images have to have the same reading order and the same size
    
    Is wise exclude the nodata values
    """
    
    import numpy
    from glass.rd.rst import rst_to_array
    
    vx = rst_to_array(x, flatten=True, with_nodata=False)
    vy = rst_to_array(y, flatten=True, with_nodata=False)
    
    
    cof = numpy.corrcoef(vx, vy)[0, 1]
    
    return cof


def speraman_correlation(x, y):
    """
    Speraman correlation between two raster images
    
    The images have to have the same reading order and the same size
    Is wise exclude the nodata values
    """
    
    from scipy         import stats
    from glass.rd.rst import rst_to_array
    
    vx = rst_to_array(x, flatten=True, with_nodata=False)
    vy = rst_to_array(y, flatten=True, with_nodata=False)
    
    coef = stats.spearmanr(vx, vy, axis=0)
    
    return coef[0]

