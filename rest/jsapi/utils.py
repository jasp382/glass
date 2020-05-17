"""
Generic Utilities
"""

from gasp3 import __import


def get_rqst_id(rqst):
    from gasp3.pyt.tm import now_as_int
    
    # Get User Info
    #requestAuth = rqst.user.username
    #userCls = __import('django.contrib.auth.models.User')
    #authObj = userCls.objects.get(username=requestAuth)
    
    return int("{}{}".format(1, now_as_int()))

