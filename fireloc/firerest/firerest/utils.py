"""
Some generic utilities
"""

from rest_framework import status


def check_rqst_param(expected, realparams):
    """
    Check request parameters

    expected - list with keys of expected parameters
    realparams - dict with parameters
    """

    r, h = None, None

    for p in expected:
        if p not in realparams:
            r, h = {
                "code"    : 'E01',
                "message" : (
                    f"Missing mandatory key in request.data; "
                    f"{p} is not in request"
                )
            }, status.HTTP_400_BAD_REQUEST
        
        if r: break
    
    return r, h

