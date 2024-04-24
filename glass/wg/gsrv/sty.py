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
    
    out = None

    try:
        r = rq.get(
            url, headers={'Accept': 'application/json'},
            auth=(conf['USER'], conf['PASSWORD'])
        )
    
    except Exception as e:
        out = {"status" : -1, "http" : None, "data" : e}
    
    if not out:
        out = {"http" : r.status_code}

        if r.status_code == 200:
            out["status"] = 1

            styles = r.json()

            if 'style' in styles['styles']:
                out["data"] = [style['name'] for style in styles['styles']['style']]
            
            else:
                out["data"] = []
        
        else:
            out["data"] = r.content
            out["status"] = 0
    
    return out


def del_style(name):
    """
    Delete a specific style
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']
    
    url = (
        f'{_p}://{h}:{p}/geoserver/rest/styles/{name}?'
        'recurse=true'
    )

    out = None

    try:
        r = rq.delete(url, auth=(conf['USER'], conf['PASSWORD']))
    
    except Exception as e:
        out = {"status" : -1, "http" : None, "data" : str(e)}
    
    if not out:
        out = {"http" : r.status_code, "data" : None}

        if r.status_code == 200:
            out["status"] = 1
        
        else:
            out["status"] = 0
            out["data"] = str(r.content)
    
    return out


def create_style(name, sld, overwrite=None):
    """
    Import SLD into a new Geoserver Style
    """

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']

    out = None
    
    if overwrite:
        rstyl = lst_styles()

        if rstyl["status"] < 1:
            out = rstyl
        
        if not out and name in rstyl["data"]:
            rdel = del_style(name)

            if rdel["status"] < 1:
                out = rdel
    
    if not out:
        url = f'{_p}://{h}:{p}/geoserver/rest/styles'

        xml = (
            f"<style><name>{name}</name><filename>"
            f"{os.path.basename(sld)}</filename></style>"
        )

        try:
            r = rq.post(
                url, data=xml,
                headers={'content-type': 'text/xml'},
                auth=(conf['USER'], conf['PASSWORD'])
            )

            if r.status_code != 201:
                out = {"status" : 0, "http" : r.status_code, "data" : str(r.content)}
        
        except Exception as e:
            out = {"status" : -1, "http" : None, "data" : e}
    
    if not out:
        url = f'{_p}://{h}:{p}/geoserver/rest/styles/{name}'

        try:
            with open(sld, 'rb') as f:
                r = rq.put(
                    url, data=f,
                    headers={'content-type': 'application/vnd.ogc.sld+xml'},
                    auth=(conf['USER'], conf['PASSWORD'])
                )

                if r.status_code == 200:
                    out = {"status" : 1, "http" : r.status_code, "data" : {"style" : name}}
                
                else:
                    out = {"status" : 0, "http" : r.status_code, "data" : str(r.content)}
        
        except Exception as e:
            out = {"status" : -1, "http" : None, "data" : e}
    
    return out


def assign_style_to_layer(style, layer):
    """
    Add a style to a geoserver layer
    """

    import json

    conf = con_gsrv()

    _p, h, p = conf['PROTOCOL'], conf['HOST'], conf['PORT']

    url = f'{_p}://{h}:{p}/geoserver/rest/layers/{layer}/styles'

    try:
        r = rq.post(
            url,
            data=json.dumps({'style' : {'name': style}}),
            headers={'content-type': 'application/json'},
            auth=(conf['USER'], conf['PASSWORD'])
        )

        out = {"http" : r.status_code}

        if r.status_code == 201:
            out["status"] = 1
            out["data"]   = {"style" : style, "layer" : layer}
        
        else:
            out["status"] = 0
            out["data"] = str(r.content)
    
    except Exception as e:
        out = {"status" : -1, "http" : None, "data" : e}

    return out


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
