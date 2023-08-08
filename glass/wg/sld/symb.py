"""
Symbolizer for Geometries
"""

def get_sld_geom_symbolizer(geom, color, opacity=None, polyStroke=None,
                            strokeWidth=None):
    """
    Return symbolic options for a specific geometric type
    
    geom should be one of the following:
    * Polygon
    * Line
    """
    
    if geom == 'Polygon':
        symbolizer = {'sld:PolygonSymbolizer' : {}}
        if opacity:
            symbolizer['sld:PolygonSymbolizer']['sld:Fill'] = {
                ('sld:CssParameter', 'name', 'fill'): str(color),
                ('sld:CssParameter', 'name', 'fill-opacity'): str(opacity)
            }
        
        else:
            symbolizer['sld:PolygonSymbolizer']['sld:Fill'] = {
                ('sld:CssParameter', 'name', 'fill'): str(color)
            }
        
        if polyStroke:
            width = '1' if not strokeWidth else str(strokeWidth)
            symbolizer['sld:PolygonSymbolizer']['sld:Stroke'] = {
                ('sld:CssParameter', 'name', 'stroke') : str(polyStroke),
                ('sld:CssParameter', 'name', 'stroke-width') : width
            }
        
        return symbolizer
    
    elif geom == 'Line':
        return {
            'sld:LineSymbolizer' : {
                'sld:Stroke' : {
                    ('sld:CssParameter', 'name', 'stroke') : str(color)
                }
            }
        }
    
    else:
        raise ValueError('Given geometry is not valid')

