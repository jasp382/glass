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
    from arcpy import env
    from arcpy.sa import *
    
    from glass.pys.oss import fprop
    
    arcpy.CheckOutExtension('Spatial')
    
    from glass.g.prop import vector_formats, raster_formats
    from gesri.rd.rst import rst_to_lyr
    from gesri.rd.shp import shp_to_lyr

    fp = fprop(outRst, ['fn', 'ff'])
    fn, ff = fp['filename'], fp['fileformat']
    
    path_to_output = outRst if not boundary else os.path.join(
        os.path.dirname(outRst), f'{fn}_ext{ff}'
    )
    
    inputFormat = os.path.splitext(shpRst)[1]
    if inputFormat in vector_formats():
        inLyr = shp_to_lyr(shpRst)
    
    elif inputFormat in raster_formats():
        inLyr = rst_to_lyr(shpRst)
    
    else:
        raise ValueError(
            'Could not identify if shpRst is a feature class or a raster'
        )
    
    if template:
        tempEnvironment0 = env.extent
        env.extent = template
    
    if snap:
        tempSnap = env.snapRaster
        env.snapRaster = snap
    
    outEucDistance = EucDistance(inLyr, "", cellsize, "")
    outEucDistance.save(path_to_output)
    
    if template: env.extent = tempEnvironment0
    
    if snap: env.snapRaster = tempSnap
    
    if boundary:
        from glass.cpu.arcg.mng.rst.proc import clip_raster
        
        clipLyr = shp_to_lyr(boundary)
        
        clip_raster(path_to_output, clipLyr, outRst,
                    template=template, snap=snap)


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

