"""
Clip rasters with ArcGIS
"""

import arcpy

def clip_rst(rst, feat_clip, out, template=None, snap=None, clipGeom=True):
    """
    Clip a single raster dataset
    """
    
    if template:
        arcpy.env.extent = template
    
    if snap:
        arcpy.env.snapRaster = snap
    
    clipGeom = "ClippingGeometry" if clipGeom else "NONE"
    arcpy.Clip_management(
        rst, "", out, feat_clip, "#",
        clipGeom, "NO_MAINTAIN_EXTENT"
    )
    
    if template:
        arcpy.env.extent = None
    
    if snap:
        arcpy.env.snapRaster = None
    
    return out


def clip_rst_each_featcls(raster, clipFolder, outputFolder,
    template=None, snap=None,
    clipGeometry=None, clipFormat='.shp',
    outputFormat='.tif', useFileID=None):
    """
    Clip a raster for each feature class in a folder
    """
    
    import os
    from glass.pys.oss import lst_ff, fprop
    
    clipShp = lst_ff(clipFolder, file_format=clipFormat)
    
    outputFormat = outputFormat if outputFormat[0] == '.' else \
        '.' + outputFormat
    
    rst_fn = None if not useFileID else fprop(raster, 'fn', forceLower=True)
    for shp in clipShp:
        fn = "{}{}".format(
            fprop(shp, 'fn', forceLower=True), outputFormat
        ) if not useFileID else "{}_{}{}".format(
            rst_fn, fprop(shp, 'fn', forceLower=True).split('_')[-1],
            outputFormat
        )
        clip_rst(raster, shp, os.path.join(
            outputFolder, fn
        ), clipGeom=clipGeometry, template=template, snap=snap
    )

    return outputFolder


def clip_rst_by_id(rst, lmt_folder, out_folder, snap_folder=None, snap_rst=None,
    ext_folder=None):
    """
    Clip Rasters in Folder using shape in other folder

    Use ID in filename to get correspondence
    """

    import os
    import pandas      as pd
    from glass.pys.oss import lst_ff

    # List Rasters
    rst_s = [{
        'fid' : int(f.split('.')[0].split('_')[-1]),
        'rst' : f
    } for f in lst_ff(
        rst, rfilename=True, file_format='.tif'
    )] if os.path.isdir(rst) else rst if type(rst) == list else None

    # List Clip Files
    lmt_s = [{
        'jfid' : int(c.split('.')[0].split('_')[-1]),
        'shp' : c
    } for c in lst_ff(
        lmt_folder, rfilename=True, file_format='.shp'
    )]

    # List files for snap or processing extent
    snaps = None if not snap_folder and not ext_folder else [{
        'sfid' : int(s.split('.')[0].split('_')[-1]),
        'snap' : s
    } for s in lst_ff(
        ext_folder if ext_folder else snap_folder,
        rfilename=True, file_format='.tif'
    )]

    # Data To Df
    if rst_s:
        df  = pd.DataFrame(rst_s)
        jdf = pd.DataFrame(lmt_s)

        df = df.merge(jdf, how='left', left_on='fid', right_on='jfid')
    
    else:
        df = pd.DataFrame(lmt_s)
        df['fid'] = df.jfid
        df['rst'] = os.path.splitext(os.path.basename(rst))[0]
        df['rst'] = df.rst.astype(str) + '_' + df.fid.astype(str) + '.tif'

    # Add snap raster to df
    if snap_folder or ext_folder:
        snap_ext = True
        sdf = pd.DataFrame(snaps)
        df = df.merge(sdf, how='left', left_on='fid', right_on='sfid')
    else:
        snap_ext = None
    
    for idx, row in df.iterrows():
        if pd.isna(row.shp):
            continue

        if snap_rst and not snap_ext:
            sr = snap_rst
        elif not snap_rst and snap_ext:
            sr = None if pd.isna(row.snap) else os.path.join(
                ext_folder if ext_folder else snap_folder, row.snap)
        elif snap_rst and snap_ext:
            sr = None if pd.isna(row.snap) else os.path.join(
                ext_folder if ext_folder else snap_folder, row.snap)
        else:
            sr = None
        
        clip_rst(
            os.path.join(
                rst if os.path.isdir(rst) else os.path.dirname(rst[idx]) \
                    if type(rst) == list else os.path.dirname(rst),
                row.rst
            ),
            os.path.join(lmt_folder, row.shp),
            os.path.join(out_folder, row.rst),
            template=None if not ext_folder else sr, clipGeom=True,
            snap=sr if not ext_folder else None
        )
    
    return out_folder

