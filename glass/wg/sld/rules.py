"""
Get Rules for SLD
"""

def style_prop(instance, mapKeys):
    """
    Return colors for this class
    """
    
    from glass.pys.clr import rgb_to_hex
    
    # Get Color
    if 'hex' in mapKeys:
        __hex = instance[mapKeys['hex']]
    else:
        __hex = rgb_to_hex(
            instance[mapKeys['r']], instance[mapKeys['g']],
            instance[mapKeys['b']]
        )
    
    # Get Stroke Color
    if 'stroke_r' not in mapKeys and 'stroke_hex' not in mapKeys:
        # Stroke will assume the same color of the geometry
        __stroke = __hex
    else:
        if 'stroke_hex' in mapKeys:
            __stroke = instance[mapKeys['stroke_hex']]
        else:
            __stroke = rgb_to_hex(
                instance[mapKeys['stroke_r']],
                instance[mapKeys['stroke_g']], instance[mapKeys['stroke_b']]
            )
    
    # Get Stroke Width
    __width = None if 'width' not in mapKeys else \
        instance[mapKeys['width']]
    
    # Get Opacity
    __opacity = "1" if 'opacity' not in mapKeys else \
        instance[mapKeys['opacity']]
    
    return __hex, __stroke, __width, __opacity


def get_categorical_rules(attr_val_color, attr_name, geometry, map_keys):
    """
    Get Rules for categorical data
    """
    
    from .symb import get_sld_geom_symbolizer

    sldRules = {}
    nr_rules = 1

    for cls in attr_val_color:
        # Get Color, Stroke color, Stroke Width Opacity
        __hex, __stroke, __width, __opacity = style_prop(cls, map_keys)
        
        sldRules[(nr_rules, 'sld:Rule')] = {
            'sld:Name'   : 'rule{}'.format(str(nr_rules)),
            'sld:Title'  : str(cls[map_keys['category']]),
            'ogc:Filter' : {
                'ogc:PropertyIsEqualTo' : {
                    'ogc:PropertyName': str(attr_name),
                    'ogc:Literal'     : str(cls[map_keys['category']])
                }
            }
        }

        sldRules[(nr_rules, 'sld:Rule')].update(
            get_sld_geom_symbolizer(
                geometry, __hex, opacity=__opacity,
                polyStroke=__stroke,
                strokeWidth=__width 
            )
        )

        nr_rules += 1

    return sldRules


def get_quantitative_rules(colorIntervals, attr_name, geometry, map_keys):
    """
    Get Rules for quantitative data
    """
    
    from .symb import get_sld_geom_symbolizer

    sldRules = {}
    nr_rules = 1

    for cls in colorIntervals:
        # Get Color, Stroke color, Stroke Width Opacity
        __hex, __stroke, __width, __opacity = style_prop(cls, map_keys)
        
        if nr_rules == 1:
            first_hex     = __hex
            first_stroke  = __stroke
            first_with    = __width
            first_opacity = __opacity

        # Create rule tree
        sldRules[(nr_rules, 'sld:Rule')] = {
            'sld:Name'   : f'rule{str(nr_rules)}',
            'sld:Title'  : (
                f'{str(cls[map_keys["interval_min"]])}..'
                f'{str(cls[map_keys["interval_max"]])}'
            ),
            'ogc:Filter' : {
                'ogc:And' : {
                    'ogc:PropertyIsGreaterThan' : {
                        'ogc:PropertyName' : str(attr_name),
                        'ogc:Literal'      : str(cls[map_keys['interval_min']])
                        },
                    'ogc:PropertyIsLessThanOrEqualTo' : {
                        'ogc:PropertyName' : str(attr_name),
                        'ogc:Literal'      : str(cls[map_keys['interval_max']])
                    }
                }
            }
        }

        sldRules[(nr_rules, 'sld:Rule')].update(
            get_sld_geom_symbolizer(
                geometry, __hex, opacity=__opacity,
                polyStroke=__stroke,
                strokeWidth=__width
            )
        )

        nr_rules += 1
    
    sldRules[(nr_rules, 'sld:Rule')] = {
        'sld:Name'   : f'rule{str(nr_rules)}',
        'sld:Title'  : 'minimum',
        'ogc:Filter' : {
            'ogc:PropertyIsEqualTo' : {
                'ogc:PropertyName' : str(attr_name),
                'ogc:Literal'      : str(colorIntervals[0][map_keys['interval_min']])
            }
        }
    }
    
    sldRules[(nr_rules, 'sld:Rule')].update(
        get_sld_geom_symbolizer(
            geometry, first_hex, opacity=__opacity,
            polyStroke=first_stroke,
            strokeWidth=first_with
        )
    )

    return sldRules

