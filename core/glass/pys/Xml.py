"""
Parse xml data
"""

import xml.etree.cElementTree as ET


def get_subElement_def(node, child):
    """
    Create a xml Tree SubElement object depending on the type of the child
    argument
    """
    
    if type(child) == tuple:
        if type(child[0]) == int:
            if len(child) == 2:
                child_element = ET.SubElement(node, child[1])
            elif len(child) >= 4:
                child_element = ET.SubElement(
                    node, child[1],
                    {child[i] : child[i+1] for i in range(2, len(child), 2)}
                )
        
        else:
            child_element = ET.SubElement(
                node, child[0],
                {child[i] : child[i+1] for i in range(1, len(child), 2)}
            )
    
    else:
        child_element = ET.SubElement(node, child)
    
    return child_element


def add_subElements_recursevely(node_element, node_name, sub_elements,
                                subElementsOrder={}):
    """
    Add elements recursevely
    """
    if node_name in subElementsOrder:
        sub_elements_order = subElementsOrder[node_name]
    else:
        sub_elements_order = list(sub_elements.keys())
    
    for child in sub_elements_order:
        child_element = get_subElement_def(node_element, child)
        if type(sub_elements[child]) != dict:
            child_element.text = sub_elements[child]
        else:
            add_subElements_recursevely(
                child_element, child, sub_elements[child],
                subElementsOrder=subElementsOrder
            )
    
    
def write_xml_tree(nodes, xml_file, nodes_order={}):
    """
    Write xml tree in a file
    
    Input nodes:
    nodes = {
        sld:Rule : {
            sld:Name : rule22,
            sld:Title: 92000,
            ogc:Filter: {
                ogc:PropertyIsEqualTo: {
                    ogc:PropertyName: code2006,
                    ogc:Literal: 92000
                }
            },
            sld:PolygonSymbolizer : {
                sld:Fill : {
                    (sld:CssParameter, name, fill): #000000,
                    (sld:CssParameter, name, fill-opacity): 0.5
                }
            }
        },
        ...
    }
    
    Output:
    <sld:Rule>
        <sld:Name>rule22</sld:Name>
        <sld:Title>92000</sld:Title>
        <ogc:Filter>
            <ogc:PropertyIsEqualTo>
                <ogc:PropertyName>code2006</ogc:PropertyName>
                <ogc:Literal>92000</ogc:Literal>
            </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        <sld:PolygonSymbolizer>
            <sld:Fill>
                <sld:CssParameter name="fill">#000000</sld:CssParameter>
                <sld:CssParameter name="fill-opacity">0.5</sld:CssParameter>
            </sld:Fill>
        </sld:PolygonSymbolizer>
    </sld:Rule>
    """
    
    # Count root nodes: only one is allowed
    if len(nodes.keys()) != 1:
        raise ValueError(
            'Only one root node is allowed when creating a xml tree')
    
    # Get root element identification
    root = list(nodes.keys())[0]
    
    if type(root) != tuple:
        root_element = ET.Element(root)
    else:
        root_element = ET.Element(
            root[0],
            {root[i]: root[i+1] for i in range(1, len(root), 2)}
        )
    
    add_subElements_recursevely(
        root_element, root, nodes[root], nodes_order
    )
    
    xml_tree = ET.ElementTree(root_element)
    xml_tree.write(xml_file, encoding='UTF-8')
    
    return xml_file

