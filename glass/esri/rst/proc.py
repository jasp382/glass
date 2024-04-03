
def clip_each_feature(rst, shp,
                      feature_id,
                      work, out_basename):
    """
    Clip a raster dataset for each feature in a feature class
    """

    import arcpy
    import os

    from glass.esri.rd.shp       import shp_to_lyr
    from glass.esri.rd.rst        import rst_to_lyr
    from glass.cpu.arcg.anls.exct import select_by_attr
    from glass.pys.oss            import mkdir

    # ########### #
    # Environment #
    # ########### #
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = work

    # ###### #
    # Do it! #
    # ###### #
    # Open feature class
    lyr_shp = shp_to_lyr(shp)
    lyr_rst = rst_to_lyr(rst)

    # Create folder for some temporary files
    wTmp = mkdir(os.path.join(work, 'tmp'))

    # Get id's field type
    fields = arcpy.ListFields(lyr_shp)
    for f in fields:
        if str(f.name) == str(feature_id):
            fld_type = f.type
            break
    
    expression = '{fld}=\'{_id}\'' if str(fld_type) == 'String' else \
        '{fld}={_id}'
    
    del fields, f

    # Run the clip tool for each feature in the shp input
    c = arcpy.SearchCursor(lyr_shp)
    l = c.next()
    while l:
        fid = str(l.getValue(feature_id))
        selection = select_by_attr(
            lyr_shp,
            expression.format(fld=feature_id, _id=fid),
            os.path.join(wTmp, f'each_{fid}.shp')
        )

        clip_rst = clip_raster(
            lyr_rst, selection, '{b}_{_id}.tif'.format(b=out_basename, _id=fid) 
        )

        l = c.next()


def clip_several_each_feature(rst_folder, shp, feature_id, work, template=None,
                              rst_file_format='.tif'):
    """
    Clip a folder of rasters by each feature in a feature class

    The rasters clipped for a feature will be in an individual folder
    """

    import arcpy
    import os

    from glass.esri.rd.shp      import shp_to_lyr
    from glass.esri.rd.rst       import rst_to_lyr
    from glass.cpu.arcg.anls.exct import select_by_attr
    from glass.esri.prop.cols  import type_fields
    from glass.pys.oss            import lst_ff, mkdir

    # ########### #
    # Environment #
    # ########### #
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = work

    # ###### #
    # Do it! #
    # ###### #
    # Open feature class
    lyr_shp = shp_to_lyr(shp)

    # Create folder for some temporary files
    wTmp = mkdir(os.path.join(work, 'tmp'))

    # Split feature class in parts
    c = arcpy.SearchCursor(lyr_shp)
    l = c.next()
    features = {}

    # Get id's field type
    fld_type = type_fields(lyr_shp, field=feature_id)

    expression = '{fld}=\'{_id}\'' if str(fld_type) == 'String' else \
        '{fld}={_id}'

    del fields, f

    while l:
        fid = str(l.getValue(feature_id))

        selection = select_by_attr(
            lyr_shp,
            expression.format(fld=feature_id, _id=fid),
            os.path.join(wTmp, 'each_{}.shp'.format(fid))
        )
        
        f_lyr = shp_to_lyr(selection)
        features[fid] = f_lyr

        l=c.next()

    rasters = lst_ff(rst_folder, file_format='.tif')

    for raster in rasters:
        r_lyr = rst_to_lyr(raster)
        for feat in features:
            clip_rst = clip_raster(
                r_lyr, features[feat],
                os.path.join(
                    work, os.path.splitext(os.path.basename(feat))[0],
                    os.path.basename(raster)
                ),
                template
            )


"""
Tools for Resampling
"""

def rst_resampling(inRst, outRst, outCell, template=None,
                   technique=None):
    """
    Change the spatial resolution of your raster dataset and set rules for
    aggregating or interpolating values across the new pixel sizes.
    
    technique options:
    * NEAREST
    * MAJORITY
    * BILINEAR
    * CUBIC
    """
    
    import os
    from glass.pys import obj_to_lst
    
    inRst = obj_to_lst(inRst)
    
    # Get outputs
    outRst = obj_to_lst(outRst)
    
    if len(inRst) != len(outRst):
        from glass.pys.oss import get_filename
        
        OUT_FOLDER = outRst[0] if os.path.isdir(outRst[0]) else \
            os.path.dirname(outRst[0]) if os.path.isfile(outRst[0]) else \
            None
        
        if not OUT_FOLDER:
            raise ValueError('outRst value is not valid')
        
        outRst = [os.path.join(OUT_FOLDER, get_filename(i) + '.tif') for i in inRst]
        
        for i in range(len(inRst)):
            if inRst[i] == outRst[i]:
                outRst[i] = os.path.join(OUT_FOLDER, "res_{}.tif".format(
                    get_filename(outRst[i])))
    
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    technique = "NEAREST" if not technique else technique
    
    CELLSIZE = "{a} {a}".format(a=str(outCell))
    for i in range(len(inRst)):
        arcpy.Resample_management(
            inRst[i], outRst[i], CELLSIZE, technique
        )
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return outRst

