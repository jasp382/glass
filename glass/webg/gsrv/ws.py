"""
Tools for Geoserver workspaces management
"""


def lst_ws():
    """
    Return a list with all avaiable workspaces in the GeoServer
    """
    
    import requests
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()

    url = '{pro}://{host}:{port}/geoserver/rest/workspaces'.format(
        host=conf['HOST'], port=conf['PORT'], pro=conf['PROTOCOL']
    )

    r = requests.get(
        url, headers={'Accept': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    workspaces = r.json()
    if 'workspace' in workspaces['workspaces']:
        return [w['name'] for w in workspaces['workspaces']['workspace']]
    else:
        return []


def del_ws(name):
    """
    Delete an existing GeoServer Workspace 
    """
    
    import requests;    import json
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()

    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{work}?'
        'recurse=true'
    ).format(
        host=conf['HOST'], port=conf['PORT'], work=name,
        pro=conf['PROTOCOL']
    )

    r = requests.delete(
        url,
        auth=(conf['USER'], conf['PASSWORD'])
    )

    return r


def create_ws(name, overwrite=True):
    """
    Create a new Geoserver Workspace
    """
    
    import requests;     import json
    from glass.cons.gsrv import con_gsrv

    conf = con_gsrv()

    url = '{pro}://{host}:{port}/geoserver/rest/workspaces'.format(
        host=conf['HOST'], port=conf['PORT'], pro=conf['PROTOCOL']
    )
    
    if overwrite:
        GEO_WORK = lst_ws()
        if name in GEO_WORK:
            del_ws(name)

    r = requests.post(
        url,
        data=json.dumps({'workspace': {'name' : name}}),
        headers={'content-type': 'application/json'},
        auth=(conf['USER'], conf['PASSWORD'])
    )

    return r

