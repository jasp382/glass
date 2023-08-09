"""
Density tools
"""

from glass.pys  import execmd


def kernel_density(pnt_feat, popField, radius, template, outRst):
    """
    Kernel density estimation. If any point is currently 
    in selection only selected points are taken into account.
    """
    
    import os
    from glass.it.rst   import saga_to_tif
    from glass.prop.rst import rst_ext, rst_cellsize
    from glass.pys .oss import fprop
    
    left, right, bottom, top = rst_ext(template)
    cellsize = rst_cellsize(template)
    
    SAGA_RASTER = os.path.join(
        os.path.dirname(outRst),
        f'saga_{fprop(outRst, "fn")}.sgrd'
    )
    
    cmd = (
        f"saga_cmd grid_gridding 6 -POINTS {pnt_feat} -POPULATION {popField} "
        f"-RADIUS {str(radius)} -TARGET_DEFINITION 0 -TARGET_USER_SIZE {str(abs(cellsize))} "
        f"-TARGET_USER_XMIN {str(left)} -TARGET_USER_XMAX {str(right)} "
        f"-TARGET_USER_YMIN {str(bottom)} -TARGET_USER_YMAX {str(top)} "
        f"-TARGET_OUT_GRID {SAGA_RASTER}"
    )
    
    outcmd = execmd(cmd)
    
    # Convert to tiff
    saga_to_tif(SAGA_RASTER, outRst)
    
    return outRst


def loop_kernel_density(points, radius, template):
    """
    Run Kernel Density in loop
    """
    
    import os
    
    for shp in points:
        for rad in radius:
            kernel_density(
                shp, points[shp]["FIELD"], rad, template, 
                os.path.join(
                    points[shp]["OUTPUT_FOLDER"],
                    f'{os.path.splitext(os.path.basename(shp))[0]}_{str(rad)}.tif'
                )
            )


def kernel_density_for_field(points, fields, radius, folderoutput, template):
    """
    Run Kernel Density for every field in fields
    """
    
    import os; from glass.pys  import obj_to_lst
    
    fields = obj_to_lst(fields)
    
    if not fields: raise ValueError('fields value is not valid')
    
    for field in fields:
        kernel_density(
            points, field, radius, template,
            os.path.join(
                folderoutput,
                os.path.splitext(os.path.basename(points))[0] + '_{}.tif'.format(field)
            )
        )

