"""
Distance tools
"""

import arcpy


def euclidean_distance(shpRst, cellsize, outRst, template=None,
                       boundary=None, snap=None):
    """
    Euclidean distance from Spatial Analyst
    """
    
    import os
    from arcpy.sa import EucDistance
    
    from glass.pys.tm import now_as_str
    from glass.pys.oss import fprop
    
    #arcpy.CheckOutExtension('Spatial')
    
    from glass.prop.df import vector_formats, raster_formats
    from glass.esri.rd.rst  import rst_to_lyr
    from glass.esri.rd.shp  import shp_to_lyr

    fp = fprop(outRst, ['fn', 'ff'])
    fn, ff = fp['filename'], fp['fileformat']
    
    path_to_output = outRst if not boundary else os.path.join(
        os.path.dirname(outRst), f'{fn}_ext{ff}'
    )
    
    inputFormat = os.path.splitext(shpRst)[1]
    if inputFormat in vector_formats():
        inLyr = shp_to_lyr(shpRst, lyrname=f'ilyr_{now_as_str(utc=True)}')
    
    elif inputFormat in raster_formats():
        inLyr = rst_to_lyr(shpRst, lyrname=f'ilyr_{now_as_str(utc=True)}')
    
    else:
        raise ValueError(
            'Could not identify if shpRst is a feature class or a raster'
        )
    
    if template:
        arcpy.env.extent = template
    
    if snap:
        arcpy.env.snapRaster = snap
    
    outEucDistance = EucDistance(inLyr, "", cellsize, "")
    outEucDistance.save(path_to_output)
    
    if boundary:
        from glass.esri.rst.ovl import clip_rst
        
        clipLyr = shp_to_lyr(boundary, lyrname=now_as_str(utc=True))
        
        clip_rst(
            path_to_output, clipLyr, outRst,
            template=template, snap=snap)
    
    if template:
        arcpy.env.extent = None
    
    if snap:
        arcpy.env.snapRaster = None
    
    return outRst


def euclidean_dist_for_multiple_extent(inFeatRst, FolderextentShp,
                                       cellsize, outFolder,
                                       snapRst=None, outputFormat='.tif'):
    """
    Execute euclidean distance for every feature class in a folder
    
    These feature will work as extent of the distance raster
    """
    
    import arcpy
    import os
    
    arcpy.env.workspace = FolderextentShp
    
    featClasses = arcpy.ListFeatureClasses()
    
    outputFormat = outputFormat if outputFormat[0] == '.' else \
        '.' + outputFormat
    
    for fc in featClasses:
        euclidean_distance(
            inFeatRst, cellsize,
            os.path.join(outFolder, 'dist_{}{}'.format(
                os.path.splitext(os.path.basename(fc))[0], outputFormat
            )),
            template=fc,
            snap=snapRst,
            boundary=os.path.join(FolderextentShp, fc)
        )


def cost_distance(supCst, pntOrigins, output, template=None):
    """
    Execute ArcGIS Cost Distance
    """
    
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = superficie_cst
    
    arcpy.gp.CostDistance_sa(supCst, pntOrigins, output, "", "")
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return output

