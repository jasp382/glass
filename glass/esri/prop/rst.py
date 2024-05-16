"""
Get Raster properties
"""

import arcpy
import os

def rst_geoprop(raster):
    """
    Return lowerLeft and cellsize
    """

    irst = arcpy.Raster(raster)

    lwleft = arcpy.Point(irst.extent.XMin, irst.extent.YMin)

    csize = irst.meanCellWidth

    return lwleft, csize


def checkIfRstIsLayer(obj):
    """
    Check if an object is a Raster Layer
    """
    
    dataType = arcpy.Describe(obj)
    
    return True if dataType == 'RasterLayer' else None


def rst_ext(rst):
    """
    Return a array with the extent of one raster dataset
    
    array order = Xmin (left), XMax (right), YMin (bottom), YMax (top)
    """
    
    extent = ["LEFT", "RIGHT", "BOTTOM", "TOP"]
    
    for i in range(len(extent)):
        v = arcpy.GetRasterProperties_management(
            rst, extent[i]
        )
            
        extent[i] = float(str(v).replace(',', '.'))
    
    return extent

def rst_ext2(rst):
    """
    Return a array with the extent of one raster dataset
    
    array order = Xmin (left), XMax (right), YMin (bottom), YMax (top)
    """
    
    describe = arcpy.Describe(rst)
        
    extent = [
        describe.extent.XMin, describe.extent.XMax,
        describe.extent.YMin, describe.extent.YMax
    ]
    
    return extent


def get_cellsize(rst, xy=False, bnd=None):
    """
    Return cellsize of one or more Raster Datasets
    
    In the case of groups, the result will be:
    d = {
        'path_to_raster1': cellsize_raster_1,
        'path_to_raster2': cellsize_raster_2,
        'path_to_raster3': cellsize_raster_3,
        ...,
        'path_to_rastern': cellsize_raster_n,
    }
    """
    
    from glass.esri.rd.rst import rst_to_lyr
    from gesri.prop.rst import checkIfRstIsLayer
    
    def _get_cell_arc(_r):
        # Check if r is a Raster Layer
        isRaster = checkIfRstIsLayer(_r)
            
        lyr = rst_to_lyr(_r) if not isRaster else _r
            
        cellsizeX = arcpy.GetRasterProperties_management(
            lyr, "CELLSIZEX", "" if not bnd else bnd
        )
                
        cellsizeY = arcpy.GetRasterProperties_management(
            lyr, "CELLSIZEY", "" if not bnd else bnd
        )
            
        if xy:
            if str(cellsizeY) != str(cellsizeX):
                raise ValueError((
                    'Cellsize is not the same in both dimensions (x, y)'
                ))
            
            else:
                return int(str(cellsizeX))
            
        else:
            return int(str(cellsizeX)), int(str(cellsizeY))
    
    def get_cellsize2(rst):
        describe = arcpy.Describe(rst)
    
        return describe.MeanCellWidth, describe.MeanCellHeight
    
    def _loop(files):
        return {f : _get_cell_arc(f) for f in files}
    
    if os.path.exists(rst):
        if os.path.isfile(rst):
            CELLSIZE = _get_cell_arc(rst)
            
            return CELLSIZE
    
        elif os.path.isdir(rst):
            from glass.pys.oss import lst_ff
        
            rsts = lst_ff(rst)
        
            return _loop(rsts)
    
        else:
            raise ValueError('The path exists but is not a file or dir')
    else:
        if type(rst) == list:
            return _loop(rst)
        
        else:
            raise ValueError((
                'Invalid object rst. Please insert a path to a raster, '
                'a path to a directory with rasters or a list with '
                'rasters path.'
            ))


def get_nodata(rst):
    """
    Return NoData Value of a raster dataset
    """
    
    desc = arcpy.Describe(rst)
    
    ndVal = desc.noDataValue
    
    return ndVal


"""
Cells Positions and Values
"""

def get_cell_value(rstLyr, x, y, xmin, ymin, cellwidth, cellheight):
    """
    Return the cell value in a raster with the x, y coordinates
    """
    
    import arcpy
    
    px = int((x - xmin) / cellwidth)
    py = int((y - ymin) / cellheight)
    
    val = arcpy.RasterToNumPyArray(rst, ncols=py, nrows=px)
    
    return val

