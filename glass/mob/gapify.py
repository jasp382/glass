
import requests as rq

from glass.cons.gapify import MAIN_URL
from glass.cons.gapify import get_gafy_token

def matrix_od(sources, dest, mode='walk'):
    """
    Matrix OD Service

    https://apidocs.geoapify.com/docs/routing/#api
    """

    key = get_gafy_token()

    headers = {
        'Content-Type'  : 'application/json'
    }

    body = {
        'mode'    : mode,
        'sources' : sources,
        'targets' : dest
    }

    url = f'{MAIN_URL}routematrix?apiKey={key}'

    rsp = rq.post(url, json=body, headers=headers)

    return rsp

