import arcpy

def line_of_sight(surfRst, lines, output):
    arcpy.ddd.LineOfSight(
        in_surface=surfRst,
        in_line_feature_class=lines, 
        out_los_feature_class=output, 
        out_obstruction_feature_class=None,
        use_curvature=None, 
        use_refraction=None,
        refraction_factor=None,
        pyramid_level_resolution=None, 
        in_features=None
    )
    
    return output

