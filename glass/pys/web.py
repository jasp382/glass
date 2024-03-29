"""
Web Tools
"""

import requests
import json

"""
From Web to Python Objects
"""


def data_from_get(url, getParams=None, auth=None):
    """
    Return json from URL - GEST Request
    """
    
    response = requests.get(
        url=url, params=getParams,
        headers={'content-type' : 'application/json'},
        auth=auth
    )
    
    return json.loads(response.text)


def http_to_json(url, ojson=None):
    """
    Data from API Endpoint to JSON File
    """

    data = data_from_get(url)

    if not ojson:
        return data
    
    else:
        with open(ojson, 'w') as ff:
            json.dump(data, ff)

        return ojson


def data_from_post(url, postdata, head='application/json',
    credentials=None):
    """
    Return data retrieve by a POST Request
    """
    
    r = requests.post(
        url, data=json.dumps(postdata),
        headers={'content-type' : head},
        auth=credentials
    )

    print(r.status_code)
    
    return r.json()


"""
Get Files from the Internet
"""

def get_file(url, output, useWget=None):
    """
    Save content of url
    """
    
    if not useWget:
        r = requests.get(url, allow_redirects=True)
    
        with open(output, 'wb') as f:
            f.write(r.content)
    
    else:
        """ On Linux Use WGET """
        
        from glass.pys import execmd
        
        outcmd = execmd(f"wget -O {output} {url}")
    
    return output


def get_file_post(url, output, params, credentials=None):
    """
    Save content of url using POST method
    """

    r  = requests.post(
        url, data=json.dumps(params),
        headers={'content-type' : 'application/json'},
        auth=credentials
    )
    
    if r.headers.get('content-type') == 'application/json':
        # It means that something went wrong
        return 0, r
    
    with open(output, 'wb') as f:
        f.write(r.content)
    
    return 1, output


def get_file_via_scp(host, username, hostpath, outpath, privateKey=None):
    """
    Get file from remote sensing via SCP
    """
    
    from glass.pys import execmd
    
    outcmd = execmd((
        f"scp {f'-i {privateKey} ' if privateKey else ''}"
        f"{username}@{host}:{hostpath} {outpath}"
    ))

