"""
Manage symbologies
"""

import arcpy


def change_simbology(mxd_path, layers, new_symbology, folder_new_project,
                     exportMap=False):

    import os
    
    if os.path.isdir(mxd_path):
        from glass.pys.oss import lst_ff
        __mxds = lst_ff(mxd_path, file_format='.mxd')
    
    elif os.path.isfile(mxd_path):
        __mxds = [mxd_path]
    
    else:
        raise ValueError(
            'mxd_path is not a file or a directory'
        )
    
    for __mxd in __mxds:
        # Open mxd
        mxd = arcpy.mapping.MapDocument(__mxd)

        lyr_template = arcpy.mapping.Layer(new_symbology)

        # List DataFrame
        __df = arcpy.mapping.ListDataFrames(mxd)

        for df in __df:
            __layers = arcpy.mapping.ListLayers(mxd, data_frame=df)
            for lyr in __layers:
                if str(lyr.name) in layers:
                    arcpy.mapping.UpdateLayer(
                        df, lyr, lyr_template, True
                    )

        if exportMap:
            arcpy.mapping.ExportToJPEG(
                mxd,
                os.path.join(
                    folder_new_project,
                    os.path.splitext(os.path.basename(__mxd))[0] + '.jpg'
                ),
                resolution=300
            )

        mxd.saveACopy(os.path.join(
            folder_new_project, os.path.basename(__mxd)
        ))

