"""
Manage data values in a Raster
"""

import arcpy


def reclassify(rst, fld, rules, out, template=None):
    """
    Reclassify a raster
    
    rules could be a str:
    '{min_range} {max_range} {new_value};...;{min_range} {max_range} {new_value}'
    OR a str:
    '{old_value} {new_value};...;{old_value} {new_value}
    
    Rules could be a dict:
    d = {
        (min_range, max_range): new_value,
        ...
        (min_range, max_range): new_value
    }
    OR a dict:
    d = {
        old_value : new_value
    }
    """
    
    arcpy.CheckOutExtension('Spatial')
    
    if type(rules) == 'str' or type(rules) == unicode:
        __rules = rules
    
    elif type(rules) == dict:
        lst_rules = []
        for k in rules:
            if type(k) == tuple:
                lst_rules.append('{} {} {}'.format(
                    str(k[0]), str(k[1]), str(rules[k])
                ))
            else:
                lst_rules.append('{} {}'.format(
                    str(k), str(rules[k])
                ))
        
        __rules = ';'.join(lst_rules)
    
    else:
        raise ValueError(('Rules type is not valid. The rules object must be'
                          ' a str or a dict'))
    
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.gp.Reclassify_sa(rst, fld, __rules, out, "DATA")
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return out


def rcls_folderRaster(rstFolder, rules, out):
    """
    Reclassify in loop for all rasters in a folder
    
    Same field, same rules for all rasters
    """
    
    import os
    
    arcpy.env.workspace = rstFolder
    
    rasters = arcpy.ListRasters()
    
    for raster in rasters:
        reclassify(
            os.path.join(rstFolder, raster), "Value", rules,
            os.path.join(out, raster), template=raster
        )
    
    return out


def lookup(inRst, fld, outRst, template=""):
    if template != "":
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    arcpy.gp.WeightedSum_sa("{r} {f} 1".format(r=inRst, f=fld), outRst)
    if template != "":
        arcpy.env.extent = tempEnvironment0
    return outRst

