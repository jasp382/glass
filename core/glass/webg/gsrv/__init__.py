"""
Dominating Geoserver with Python and requests

* the following methods may be used in Linux and MSWindows
"""


def backup(backup_file):
    """
    """
    
    import requests
    import json
    from glass.cons.gsrv import con_gsrv
    
    conf = con_gsrv()
    
    url = '{pro}://{host}:{port}/geoserver/rest/br/backup/'.format(
        host=conf['HOST'], port=conf['PORT'], pro=conf["PROTOCOL"]
    )
    
    backup_parameters = {
        "backup" : {
            "archiveFile" : backup_file,
            "overwrite":True,
            "options": {
                #"option": ["BK_BEST_EFFORT=true"]
            }
            # filter
        }
    }   
    
    r = requests.post(
        url, headers={'content-type': 'application/json'},
        data=json.dumps(backup_parameters),
        auth=(conf['USER'], conf['PASSWORD'])
    )
    
    return r
