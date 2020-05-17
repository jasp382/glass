"""
Write SLD with Python
"""


def write_sld(attr_name, attr_colors, mapAttrKeys, sld_path,
              geometry=None, DATA='CATEGORICAL'):
    """
    Write a sld file using an association between field attributes and a color

    * attr_name -> name of a column in a layer
    
    * DATA -> CATEGORICAL | QUANTITATIVE
    
    * attr_colors -> list or table with styles for some category or interval
    
    QUANTITATIVE - TABLE EXAMPLE (Sheet Index = 0):
         | min | max | R | G | B
       1 |  0  |  5  | X | X | X
       2 |  5  |  10 | X | X | X
       3 |  10 |  15 | X | X | X
       4 |  15 |  20 | X | X | X
       5 |  20 |  25 | X | X | X
       
    QUANTITATIVE - LIST EXAMPLE:
    attr_colors = [
        {'min':  0, 'max':  5, 'R': X, 'G': X, 'B': X},
        {'min':  5, 'max': 10, 'R': X, 'G': X, 'B': X},
        {'min': 10, 'max': 15, 'R': X, 'G': X, 'B': X},
        {'min': 15, 'max': 20, 'R': X, 'G': X, 'B': X},
        {'min': 20, 'max': 25, 'R': X, 'G': X, 'B': X}
    ]
    
    CATEGORICAL - TABLE EXAMPLE
    
    CATEGORICAL - LIST EXAMPLE
    
    * mapAttrKeys -> dict with the relation between the meaning of the 
    columns/keys in attr_colors
    
    EXAMPLE:
    mapAttrKeys = {
        'r' : 'R', 'g' : 'G', 'b' : 'B', 'interval_min' : 'min',
        'interval_max' : 'max'
    }
    
    keys that could be used:
    * r -> attr_colors key/column with red of red|green|blue cat color
    * g -> attr_colors key/column with green of red|green|blue cat color
    * b -> attr_colors key/column with blue of red|green|blue cat color
    * hex -> attr_colors key/column with color hex
    * interval_min -> attr_colors key/column com limiar inferior do intervalo
    * interval_max -> attr_colors key/column com limiar superior do intervalo
    * stroke_hex -> attr_colors key/column with color hex for stroke
    * stroke_r -> attr_colors key/column with red of red|green|blue stroke color
    * stroke_g -> attr_colors key/column with green of red|green|blue stroke color
    * stroke_b -> attr_colors key/column with blue of red|green|blue stroke color
    * width -> attr_colors key/column with stroke width
    * opacity -> attr_colors key/column with opacity value for some category
    * category -> attr_colors key/column with category value
    
    sld_path -> path to sld file
    
    GEOMETRY -> Polygon | Line

    NOTE: This will work only for polygon/linear features
    """

    import os; from glass.pyt.Xml   import write_xml_tree
    from glass.pyt.oss              import fprop
    from glass.web.geosrv.sld.rules import get_categorical_rules
    from glass.web.geosrv.sld.rules import get_quantitative_rules
    
    if DATA != 'CATEGORICAL' and DATA != 'QUANTITATIVE':
        raise ValueError(
            'DATA should has the value CATEGORICAL or QUANTITATIVE'
        )
    
    if type(attr_colors) != list:
        if os.path.exists(attr_colors):
            ff = fprop(attr_colors, 'ff')
            
            if ff == '.json':
                import json
                
                attr_colors = json.load(open(attr_colors, 'r'))
            
            elif ff == '.xlsx' or ff == '.xls':
                from glass.dct.fm import tbl_to_obj
                
                attr_colors = tbl_to_obj(
                    attr_colors, sheet=0, useFirstColAsIndex=None, output='array'
                )
            
            elif ff == '.dbf':
                from glass.dct.fm import tbl_to_obj
                
                attr_colors = tbl_to_obj(attr_colors, output='array')
            
            else:
                raise ValueError('Your file is not a json or a xls')
        else:
            raise ValueError((
                'ERROR in argument attribute_value_colors: '
                'You need to define a list or give a valid path to a json '
                'file or to a xls file'
            ))

    GEOMETRY = str(geometry) if geometry else 'Polygon'

    # Create Feature Type Style RULES
    sldRules = get_categorical_rules(
        attr_colors, attr_name, GEOMETRY, mapAttrKeys
    ) if DATA == 'CATEGORICAL' else get_quantitative_rules(
        attr_colors, attr_name, GEOMETRY, mapAttrKeys
    ) if DATA == 'QUANTITATIVE' else None

    # SLD Basic structure
    xml_sld_root = (
        'sld:StyledLayerDescriptor', 'xmlns', 'http://www.opengis.net/sld',
        'xmlns:sld', 'http://www.opengis.net/sld',
        'xmlns:gml', 'http://www.opengis.net/gml',
        'xmlns:ogc', 'http://www.opengis.net/ogc',
        'version', '1.0.0'
    )

    sld = {
        xml_sld_root: {
            'sld:UserLayer' : {
                'sld:LayerFeatureConstraints': {
                    'sld:FeatureTypeConstraint': ''
                },
                'sld:UserStyle': {
                    'sld:Name' : 'Default Styler',
                    'sld:IsDefault': '1',
                    'sld:FeatureTypeStyle': {
                        'sld:Name': 'group 0',
                        'sld:FeatureTypeName': 'Feature',
                        (1, 'sld:SemanticTypeIdentifier'): 'generic:geometry',
                        (2, 'sld:SemanticTypeIdentifier'): 'colorbrewer:unique:corinne'
                    }
                }
            }
        }
    }

    sld_order = {
        xml_sld_root : ['sld:UserLayer'],
        'sld:UserLayer' : ['sld:LayerFeatureConstraints', 'sld:UserStyle'],
        'sld:UserStyle' : ['sld:Name', 'sld:IsDefault', 'sld:FeatureTypeStyle'],
        'sld:FeatureTypeStyle' : ['sld:Name', 'sld:FeatureTypeName',
                                  (1, 'sld:SemanticTypeIdentifier'),
                                  (2, 'sld:SemanticTypeIdentifier')],
        'ogc:PropertyIsEqualTo' : ['ogc:PropertyName', 'ogc:Literal'],
        'ogc:And' : ['ogc:PropertyIsLessThanOrEqualTo', 'ogc:PropertyIsGreaterThan'],
        'ogc:PropertyIsLessThanOrEqualTo' : ['ogc:PropertyName', 'ogc:Literal'],
        'ogc:PropertyIsGreaterThan' : ['ogc:PropertyName', 'ogc:Literal'],
        'sld:Fill': [
            ('sld:CssParameter', 'name', 'fill'),
            ('sld:CssParameter', 'name', 'fill-opacity')
        ]
    }

    sld[xml_sld_root]['sld:UserLayer']['sld:UserStyle']['sld:FeatureTypeStyle'].update(sldRules)

    symbolizer = 'sld:PolygonSymbolizer' if GEOMETRY == 'Polygon' \
        else 'sld:LineSymbolizer' if GEOMETRY == 'Line' \
        else 'sld:PolygonSimbolizer'

    for i in range(len(sldRules.keys())):
        sld_order['sld:FeatureTypeStyle'].append((i+1, 'sld:Rule'))
        sld_order[(i+1, 'sld:Rule')] = [
            'sld:Name', 'sld:Title', 'ogc:Filter', symbolizer
        ]
    
    if GEOMETRY == 'Polygon':
        for i in range(len(sldRules.keys())):
            sld_order['sld:PolygonSymbolizer'] = ['sld:Fill', 'sld:Stroke']

    write_xml_tree(sld, sld_path, nodes_order=sld_order)

    return sld_path


def write_raster_sld(attrProp, outSld, dataType="CATEGORICAL"):
    """
    Write a SLD for a raster with categorical values
    
    attrProp = {
        raster_value : {"COLOR" : hex, "LABEL" : some_label},
        ...
    }
    
    OR
    attrProp = {
        raster_value : {
            "COLOR" : (red value, green_value, blue_value),
            "LABEL" : some_label
        },
        ...
    }
    
    dataType Options:
    * CATEGORICAL;
    * FLOATING;
    """
    
    from glass.pyt.clr import rgb_to_hex
    from glass.pyt.Xml import write_xml_tree
    
    # SLD Basic Structure
    sldRoot = (
        'sld:StyledLayerDescriptor', 'xmlns', 'http://www.opengis.net/sld',
        'xmlns:sld', 'http://www.opengis.net/sld',
        'xmlns:gml', 'http://www.opengis.net/gml',
        'xmlns:ogc', 'http://www.opengis.net/ogc',
        'version', '1.0.0'
    )
    
    # Create a propor dict with style options for every value
    attrStyleOptions = {}
    RASTER_VALUES = list(attrProp.keys())
    RASTER_VALUES.sort()
    rules_Order = []
    i = 1
    for k in RASTER_VALUES:
        # Get Color Value
        if type(attrProp[k]["COLOR"]) == list or type(attrProp[k]["COLOR"]) == tuple:
            r, g, b = attrProp[k]["COLOR"]
            hex_color = rgb_to_hex(r, g, b)
        else:
            hex_color = str(attrProp[k]["COLOR"])
        
        # Get Opacity Value
        if "OPACITY" in attrProp[k]:
            opacity = str(attrProp[k]["OPACITY"])
        else:
            opacity = "1.0"
        
        so =  (
            "sld:ColorMapEntry", "color", hex_color,
            "opacity", opacity, "quantity", str(k),
            "label", str(attrProp[k]["LABEL"])
        )
        attrStyleOptions[so] = ''
        rules_Order.append(so)
        i += 1
    
    # Get Type of Color Ramp
    TYPE_PALETE = 'ramp' if dataType == "FLOATING" else 'values' 
    
    # Create SLD Tree
    sldTree = {
        sldRoot : {
            'sld:UserLayer' : {
                'sld:LayerFeatureConstraints': {
                    'sld:FeatureTypeConstraint': ''
                },
                'sld:UserStyle' : {
                    'sld:Name'      : 'Default Styler',
                    'sld:IsDefault' : '1',
                    'sld:FeatureTypeStyle': {
                        'sld:Rule' : {
                            'sld:RasterSymbolizer' : {
                                ('sld:ColorMap', 'type', TYPE_PALETE) : attrStyleOptions
                            }
                        }
                    }
                }
            }
        }
    }
    
    sldOrder = {
        sldRoot         : ['sld:UserLayer'],
        'sld:UserLayer' : ['sld:LayerFeatureConstraints', 'sld:UserStyle'],
        'sld:UserStyle' : ['sld:Name', 'sld:IsDefault', 'sld:FeatureTypeStyle'],
        ('sld:ColorMap', 'type', TYPE_PALETE)  : rules_Order
    }
    # Write SLD file
    write_xml_tree(sldTree, outSld, nodes_order=sldOrder)
    
    return outSld

