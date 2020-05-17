"""
Collect data from IPMA
"""

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
    from glass.to.web import http_to_json

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
        http_to_json(urls[k], os.path.join(folder, '{}_{}.json'.format(k, today)))
