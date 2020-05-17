"""
Distance between points using OSRM API
"""


BASE_URL = "https://router.project-osrm.org"


def route(latOrig, lngOrig, latDest, lngDest, profile='driving'):
    """
    Get route between two points
    """

    """
    URL Parameters:
    service - One of the following values: route,
    nearest, table, match, trip, tile

    version - Version of the protocol implemented by the service.
    v1 for all OSRM 5.x installations

    profile - Mode of transportation, is determined statically by
    the Lua profile that is used to prepare the data using osrm-extract.
    Typically car, bike or foot if using one of the supplied profiles.

    coordinates - String of format
    {longitude},{latitude};{longitude},{latitude}[;{longitude},{latitude} ...]
    or polyline({polyline}) or polyline6({polyline6}).

    format - Only json is supported at the moment.
    This parameter is optional and defaults to json
    """
    
    from glass.pys.web import http_to_json
    
    URL = "{base}/route/v1/{pro}/{lng_o},{lat_o};{lng_d},{lat_d}".format(
        base=BASE_URL,
        lng_o=str(lngOrig) if ',' not in str(lngOrig) else lngOrig.replace(',', '.'),
        lat_o=str(latOrig) if ',' not in str(latOrig) else latOrig.replace(',', '.'),
        lng_d=str(lngDest) if ',' not in str(lngDest) else lngDest.replace(',', '.'),
        lat_d=str(latDest) if ',' not in str(latDest) else latDest.replace(',', ','),
        pro=profile
    )

    data = http_to_json(URL)

    return data


def nearest(lat, lng, number=1, mode='driving'):
    """
    Snaps a coordinate to the street network and returns the nearest n matches.
    """
    
    from glass.pys.web import http_to_json
    
    URL = "{base}/nearest/v1/{_mod_}/{_lat},{_lng}?number={nr}".format(
        URL=BASE_URL,
        _mod_=mode,
        _lat=str(lat) if ',' not in str(lat) else lat.replace(',', '.'),
        _lng=str(lng) if ',' not in str(lng) else lng.replace(',', '.'),
        nr=str(number)
    )
    
    data = http_to_json(URL)
    
    return data


def matrix(origins, destinations, mode='driving'):
    """
    Retrieve a distance matrix from a group of origins and
    destinations.
    
    origins and destinations = [(x, y), ..., (x, y)]
    or
    origins and destinations = '-8.052,40.052;-8.053,40.055'
    """
    
    from glass.pys.web import http_to_json
    
    def sanitize_coords(pair):
        x, y = str(pair[0]), str(pair[1])
        
        return '{},{}'.format(
            x if ',' not in x else x.replace(',', '.'),
            y if ',' not in y else y.replace(',', '.')
        )
    
    origins = str(origins) if type(origins) == str else \
        ';'.join([sanitize_coords(x) for x in origins]) \
        if type(origins) == list else None
    
    destinations = str(destinations) if type(destinations) == str else \
        ';'.join([sanitize_coords(x) for x in destinations]) \
        if type(destinations) == list else None
    
    if not origins or not destinations:
        raise ValueError('origins or destinations value is not valid')
    
    cnt = 0
    __origins = origins.split(';'); __dest = destinations.split(';')
    for i in range(len(__origins)):
        if not i:
            src = str(cnt)
        else:
            src += ';' + str(cnt)
        cnt += 1
    
    for i in range(len(__dest)):
        if not i:
            dest = str(cnt)
        else:
            dest += ';' + str(cnt)
        cnt += 1
    
    URL = "{}/table/v1/{}/{};{}?source={}&destinations={}".format(
        BASE_URL, mode, origins, destinations, src, dest
    )
    
    data = http_to_json(URL)
    
    return data

