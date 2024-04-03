"""
Hydrologic procedures
"""

import arcpy


def generate_waterlines(mdt, waterbodies, accumulation_value=500,
                        workspace=None):
    """
    Generate Water Bodies lines
    """
    
    import os
    from glass.esri.rd.rst import rst_to_lyr
    from glass.prop.df import vector_formats, raster_formats
    from glass.esri.rst.alg import rstcalc
    from glass.esri.rst.hydro import fill, flow_direction
    from glass.esri.rst.hydro import flow_accumulation, stream_to_feature
    
    workspace = workspace if workspace else \
        os.path.dirname(waterbodies)
    
    raster_format = os.path.splitext(os.path.basename(waterbodies))[1]
    
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    
    fill_rst = fill(mdt, f'flow_raster{raster_format}', template=mdt)
    
    dire_rst = flow_direction(
        fill_rst, f'direction_raster{raster_format}',
        template=mdt
    )
    
    flow_acc = flow_accumulation(
        dire_rst, f'flow_raster{raster_format}',
        template=mdt
    )
    
    # Split water bodies from the other accumulation data
    lyr_flow = rst_to_lyr(flow_acc)
    
    outFormat = os.path.splitext(os.path.basename(waterbodies))[1]
    rstFormat = raster_formats()
    vecFormat = vector_formats()
    
    waterRst = waterbodies if outFormat in rstFormat else \
        os.path.join(
            workspace,
            os.path.splitext(os.path.basename(waterbodies))[0] + raster_format
        ) if outFormat in vecFormat else None
    
    if not waterRst:
        raise ValueError('Your output is not a raster and is not a vector')
    
    waterRst = rstcalc(
        '{r} > {a}'.format(
            r=os.path.splitext(os.path.basename(flow_acc))[0],
            a=str(accumulation_value)
        ),
        waterRst, template=mdt, api='arcpy'
    )
    
    if outFormat in vecFormat:
        stream_to_feature(waterRst, dire_rst, waterbodies)
        
        return waterbodies
    
    else:
        return waterRst

