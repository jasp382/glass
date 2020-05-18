"""
Tools for Geoserver styles management
"""


def lst_styles():
    """
    List Styles in Geoserver
    """
    
    import requests
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()
    
    url = '{pro}://{host}:{port}/geoserver/rest/styles'.format(
        host=conf['HOST'], port=conf['PORT'], pro=conf['PROTOCOL']
    )
    
    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )
    
    styles = r.json()
    
    if 'style' in styles['styles']:
        return [style['name'] for style in styles['styles']['style']]
    
    else:
        return []


def del_style(name):
    """
    Delete a specific style
    """
    
    import requests; import json
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()
    
    url = (
        '{pro}://{host}:{port}/geoserver/rest/styles/{stl}?'
        'recurse=true'
    ).format(
        host=conf['HOST'], port=conf['PORT'],
        stl=name, pro=conf['PROTOCOL']
    )
    
    r = requests.delete(url, auth=(conf['USER'], conf['PASSWORD']))
    
    return r


def create_style(name, sld, overwrite=None):
    """
    Import SLD into a new Geoserver Style
    """

    import requests;    import os
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()
    
    if overwrite:
        GEO_STYLES = lst_styles()
        
        if name in GEO_STYLES:
            del_style(name)

    url = '{pro}://{host}:{port}/geoserver/rest/styles'.format(
        host=conf['HOST'], port=conf['PORT'], pro=conf['PROTOCOL']
    )

    xml = '<style><name>{n}</name><filename>{filename}</filename></style>'.format(
        n=name, filename=os.path.basename(sld)
    )

    r = requests.post(
        url,
        data=xml,
        headers={'content-type': 'text/xml'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    url = '{pro}://{host}:{port}/geoserver/rest/styles/{n}'.format(
        host=conf['HOST'], port=conf['PORT'], n=name, pro=conf['PROTOCOL']
    )

    with open(sld, 'rb') as f:
        r = requests.put(
            url,
            data=f,
            headers={'content-type': 'application/vnd.ogc.sld+xml'},
            auth=(conf['USER'], conf['PASSWORD'])
        )

        return r


def assign_style_to_layer(style, layer):
    """
    Add a style to a geoserver layer
    """

    import requests;    import json
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()

    url = '{pro}://{host}:{port}/geoserver/rest/layers/{lyr}/styles'.format(
        host=conf['HOST'], port=conf['PORT'],
        lyr=layer, pro=conf['PROTOCOL']
    )

    r = requests.post(
        url,
        data=json.dumps({'style' : {'name': style}}),
        headers={'content-type': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    return r


def add_style_to_layers_basename(style, basename):
    """
    Add a style to all layers with the same basename
    """
    
    from glass.web.geosrv.lyrs import lst_lyr

    # List layers that starts with a certain basename
    layers = lst_lyr()

    resp = []
    for lyr in layers:
        if basename in lyr:
            # Apply style to all layers in flayers
            r = assign_style_to_layer(style, lyr)
            resp.append(r)
    
    return resp


def add_style_to_layers(layers, style):
    """
    Add a style to all layers in a list
    """

    return [assign_style_to_layer(style, l) for l in layers]
