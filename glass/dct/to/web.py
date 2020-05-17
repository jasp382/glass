"""
Get Files from the Internet
"""


def get_file_ul(url, output):
    """
    Return a file from the web and save it somewhere
    """
    
    import urllib
    
    data_file = urllib.URLopener()
    
    data_file.retrieve(url, output)
    
    return output


def get_file(url, output, useWget=None):
    """
    Save content of url
    """
    
    if not useWget:
        import requests
    
        r = requests.get(url, allow_redirects=True)
    
        with open(output, 'wb') as f:
            f.write(r.content)
    
    else:
        """ On Linux Use WGET """
        
        from glass.pyt import execmd
        
        outcmd = execmd("wget -O {} {}".format(output, url))
    
    return output


def get_file_post(url, output, params, credentials=None):
    """
    Save content of url using POST method
    """

    import requests
    import json

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
    
    from glass.pyt import execmd
    
    outcmd = execmd("scp {}{}@{}:{} {}".format(
        "-i {} ".format(privateKey) if privateKey else "",
        username, host, hostpath, outpath
    ))


def http_to_json(url, ojson):
    """
    Data from API Endpoint to JSON File
    """

    import json
    from glass.dct.fm.web import data_from_get

    data = data_from_get(url)

    with open(ojson, 'w') as ff:
        json.dump(data, ff)

    return ojson
