"""
Density tools
"""

from glass.pyt import execmd


def kernel_density(pnt_feat, popField, radius, template, outRst):
    """
    Kernel density estimation. If any point is currently 
    in selection only selected points are taken into account.
    """
    
    import os
    from glass.geo.gt.torst    import saga_to_tif
    from glass.geo.gt.prop.rst import rst_ext, get_cellsize
    from glass.pyt.oss     import fprop
    
    left, right, bottom, top = rst_ext(template)
    cellsize = get_cellsize(template)
    
    SAGA_RASTER = os.path.join(
        os.path.dirname(outRst),
        'saga_{}.sgrd'.format(fprop(outRst, 'fn'))
    )
    
    cmd = (
        "saga_cmd grid_gridding 6 -POINTS {} -POPULATION {} "
        "-RADIUS {} -TARGET_DEFINITION 0 -TARGET_USER_SIZE {} "
        "-TARGET_USER_XMIN {} -TARGET_USER_XMAX {} "
        "-TARGET_USER_YMIN {} -TARGET_USER_YMAX {} "
        "-TARGET_OUT_GRID {}"
    ).format(
        pnt_feat, popField,
        str(radius), str(abs(cellsize)),
        str(left), str(right),
        str(bottom), str(top),
        SAGA_RASTER
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
                    '{}_{}.tif'.format(
                        os.path.splitext(os.path.basename(shp))[0],
                        str(rad)
                    )
                )
            )


def kernel_density_for_field(points, fields, radius, folderoutput, template):
    """
    Run Kernel Density for every field in fields
    """
    
    import os; from glass.pyt import obj_to_lst
    
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

