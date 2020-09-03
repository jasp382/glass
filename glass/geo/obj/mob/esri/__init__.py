"""
Get Travel Modes
"""

def get_tv_by_impedancetype(impedance):
    """
    Return TravelMode for the given impedance

    impedance options:
    * WalkTime
    """

    import requests as rqsts
    from glass.cons.esri import TV_URL, rest_token

    token = rest_token()

    tvs = rqsts.get(TV_URL, params={'f' : 'json', 'token' : token})

    if tvs.status_code == 200:
        tvdata = tvs.json()

        tmode = None

        for tv in tvdata.get('supportedTravelModes'):
            for r in tv['attributeParameterValues']:
                if r['attributeName'] == impedance:
                    tmode = tv
                    break
            
            if tmode:
                break
        
        return tmode
    
    else:
        raise ValueError('Something went wrong with the request!')

