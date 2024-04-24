"""
Tools for Geoserver workspaces management
"""

import requests

from glass.cons.gsrv import con_gsrv


def lst_ws():
    """
    Return a list with all avaiable workspaces in the GeoServer
    """

    G = con_gsrv()

    url = (
        f'{G["PROTOCOL"]}://{G["HOST"]}'
        f':{G["PORT"]}/geoserver/rest/workspaces'
    )

    try:
        r = requests.get(
            url, headers={'Accept': 'application/json'},
            auth=(G['USER'], G['PASSWORD'])
        )

        if r.status_code == 200:
            workspaces = r.json()

            if 'workspace' in workspaces['workspaces']:
                ws = [w['name'] for w in workspaces['workspaces']['workspace']]
            else:
                ws = []
            
            return {"status" : 1, "http" : r.status_code, "data" : ws}
        
        else:
            return {"status" : 0, "http" : r.status_code, "data" : str(r.content)}

    
    except Exception as e:
        return {"status" : -1, 'http' : None, "data" : str(e)}
    


def del_ws(name):
    """
    Delete an existing GeoServer Workspace 
    """

    conf = con_gsrv()

    url = (
        f'{conf["PROTOCOL"]}://{conf["HOST"]}:{conf["PORT"]}/'
        f'geoserver/rest/workspaces/{name}?recurse=true'
    )

    try:
        r = requests.delete(
            url,
            auth=(conf['USER'], conf['PASSWORD'])
        )

        if r.status_code == 200:
            return {"status" : 1, "http" : r.status_code, "data" : None}
        
        else:
            return {"status" : 0, "http" : r.status_code, "data" : r.content}
    
    except Exception as e:
        return {"status" : -1, "http" : None, "data" : e}


def create_ws(name, overwrite=True):
    """
    Create a new Geoserver Workspace
    """
    
    import json

    conf = con_gsrv()

    url = (
        f"{conf['PROTOCOL']}://{conf['HOST']}:{conf['PORT']}/"
        "geoserver/rest/workspaces"
    )
    
    if overwrite:
        status= lst_ws()

        if not status["status"]:
            return status
        
        geows = status["data"]
        
        if name in geows:
            dstatus = del_ws(name)

            if not dstatus["status"]:
                return dstatus
    
    try:
        r = requests.post(
            url,
            data=json.dumps({'workspace': {'name' : name}}),
            headers={'content-type': 'application/json'},
            auth=(conf['USER'], conf['PASSWORD'])
        )

        if r.status_code == 201:
            return {"status" : 1, "http" : r.status_code, "data" : {"workspace" : name}}
        
        else:
            return {"status" : 0, "http" : r.status_code, "data" : str(r.content)}
    
    except Exception as e:
        return {"status" : -1, "http" : None, "data" : str(e)}

