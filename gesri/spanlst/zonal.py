"""
MODULE: zonal statistics for arcgis
PURPOSE: Tools for calculate statistics of zones with arcgis
"""


# Calcula media de um raster por entidade geometrica
def mean_rst_by_polygon(polygons, raster, work, resultShp):
    """
    Mean of all cells intersect with the input polygon features
    """
    
    import arcpy
    import os
    
    from gesri.rd.rst import rst_to_lyr
    from gesri.rd.shp          import shp_to_lyr
    from glass.prop.rst              import rst_stats
    from gesri.tbl.cols      import add_col
    from gesri.dp               import copy_feat
    from glass.cpu.arcg.anls.exct    import select_by_attr
    from glass.cpu.arcg.mng.rst.proc import clip_raster
    
    # ########### #
    # Environment #
    # ########### #
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = work
    
    # ###### #
    # Do it! #
    # ###### #
    # Copy the Input
    poly_copy = copy_feat(polygons, resultShp, gisApi='arcpy')
    # Create Layers
    lyrShp = shp_to_lyr(poly_copy)
    lyrRst = rst_to_lyr(raster)
    # Create field for register calculated statistics
    if len(os.path.basename(raster)) <= 10:
        fld_name = os.path.basename(raster)
    else:
        fld_name = os.path.basename(raster)[:10]    
    add_col(lyrShp, fld_name, "DOUBLE", "20", "3")
    # Calculate mean
    c = arcpy.UpdateCursor(lyrShp)
    l = c.next()
    while l:
        fid = str(l.getValue("FID"))
        selection = select_by_attr(
            lyrShp,
            "FID={c}".format(c=fid),
            "poly_{c}.shp".format(c=fid)
        )
        sel_rst = clip_raster(
            lyrRst, selection, "clip_rst_{c}.img".format(c=fid))
        
        mean = rst_stats(sel_rst, api='arcpy')["MEAN"]
        l.setValue(fld_name, mean)
        c.updateRow(l)
        l = c.next()

