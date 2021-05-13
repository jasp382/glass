import numpy

def rst_to_array(r, flatten=False, with_nodata=True):
    """
    Convert Raster image to numpy array
    
    If flatten equal a True, the output will have a shape of (1, 1).
    
    If with_nodata equal a True, the output will have the nodata values
    """
    
    import arcpy
    
    img_array = arcpy.RasterToNumPyArray(r)
    
    if flatten==False and with_nodata==True:
        return img_array
    
    elif flatten==True and with_nodata==True:
        return img_array.flatten()
    
    elif flatten == True and with_nodata == False:
        rasterObj = arcpy.Raster(r)
        noData = rasterObj.noDataValue
        values = img_array.flatten()
        clean_values = numpy.delete(
            values, numpy.where(values==noData), None)
        return clean_values


