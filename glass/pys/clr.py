"""
Operations with colors
"""

def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(
        int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)
    )


def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (red, green, blue)


def idcolor_to_hex(rgbObj):
    """
    Find RGB in rgbObj and convert RGB to HEX
    """
    
    if type(rgbObj) == tuple or type(rgbObj) == list:
        _hex = rgb_to_hex(rgbObj[0], rgbObj[1], rgbObj[2])
    
    elif type(rgbObj) == dict:
        R = 'R' if 'R' in rgbObj else 'r' if 'r' in rgbObj else \
            None
        G = 'G' if 'G' in rgbObj else 'g' if 'g' in rgbObj else \
            None
        B = 'B' if 'B' in rgbObj else 'b' if 'b' in rgbObj else \
            None
        
        if not R or not G or not B:
            raise ValueError(
                ('rgbObj Value is not valid'
                 'You are using a dict to specify the color related with'
                 'each attribute categorie, but you are not using R, G and B'
                 ' as keys. Please use a dict with the following structure: '
                    '{\'R\': 255, \'R\': 255, \'R\': 255}'
                )
            )
        else:
            _hex = rgb_to_hex(rgbObj[R], rgbObj[G], rgbObj[B])
    
    elif type(rgbObj) == str:
        _hex = rgbObj
    
    else:
        raise ValueError('rgbObj value is not valid')
    
    return _hex
