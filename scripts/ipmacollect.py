"""
Collect data from IPMA
"""

import json
import requests

def data_from_get(url, getParams=None, auth=None):
    """
    GET Request - Access some URL and retrieve JSON
    data
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

    import json

    data = data_from_get(url)

    if not ojson:
        return data
    
    else:
        with open(ojson, 'w') as ff:
            json.dump(data, ff)

        return ojson

if __name__ == '__main__':
    """
    Parameters
    """

    folder = '/home/jasp/mrgis/ipma_data'

    """
    Collect data
    """

    import os
    import datetime as dt
    from glass.pys.web import http_to_json

    urls = {
        # Previsao Meteorologica Diaria ate 3 dias, informação agregada por dia - Hoje
        'prev_today' : 'https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/hp-daily-forecast-day0.json',
        # Previsao Meteorologica Diaria ate 3 dias, informação agregada por dia - Amanha
        'prev_tomorrow' :'https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/hp-daily-forecast-day1.json',
        # Previsao Meteorologica Diaria ate 3 dias, informação agregada por dia - Depois Amanha
        'prev_atomorrow' : 'https://api.ipma.pt/open-data/forecast/meteorology/cities/daily/hp-daily-forecast-day2.json',
        # Observação Meteorológica de Estações (dados horários, últimas 24 horas)
        'obs' : 'https://api.ipma.pt/open-data/observation/meteorology/stations/observations.json'
    }

    today = str(dt.datetime.now().replace(microsecond=0).date()).replace('-', '')

    for k in urls:
        http_to_json(urls[k], ojson=os.path.join(folder, '{}_{}.json'.format(k, today)))
