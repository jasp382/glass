"""
Tools for Geoserver styles management
"""

import os
import requests as rq

from glass.cons.gsrv import con_gsrv


def lst_styles():
    """
    List Styles in Geoserver
    """
    
    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = f'{_p}://{h}:{p}/geoserver/rest/styles'
    
    r = rq.get(
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

    conf = con_gsrv()
    
    url = (
        f'{conf["PROTOCOL"]}://{conf["HOST"]}:{conf["PORT"]}/'
        f'geoserver/rest/styles/{name}?recurse=true'
    )
    
    r = rq.delete(url, auth=(conf['USER'], conf['PASSWORD']))
    
    return r


def create_style(name, sld, overwrite=None):
    """
    Import SLD into a new Geoserver Style
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    if overwrite:
        GEO_STYLES = lst_styles()
        
        if name in GEO_STYLES:
            del_style(name)

    url = f'{_p}://{h}:{p}/geoserver/rest/styles'

    xml = (
        f"<style><name>{name}</name><filename>"
        f"{os.path.basename(sld)}</filename></style>"
    )

    r = rq.post(
        url,
        data=xml,
        headers={'content-type': 'text/xml'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    url = f'{_p}://{h}:{p}/geoserver/rest/styles/{name}'

    with open(sld, 'rb') as f:
        r = rq.put(
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

    import json

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']

    url = f'{_p}://{h}:{p}/geoserver/rest/layers/{layer}/styles'

    r = rq.post(
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
    
    from glass.wg.gsrv.lyr import lst_lyr

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
