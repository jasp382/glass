"""
Deal with Django Users
"""


def add_new_user(user, firstName, lastName, mail, passWord):
    """
    Create new user to Django App
    """
    # id; password; last_login; is_superuser; username; first_name;
    # last_name; email; is_staff; is_active; date_joined
    
    # TODO: Check if username already exists
    
    import datetime
    from django.contrib.auth.models import User
    from glass.pys import __import
    
    # Get User Info
    userCls = __import('django.contrib.auth.models.User')
    authFid = userCls.objects.latest('id').id + 1
    
    user = User.objects.create_user(
        username=user, email=mail, password=passWord,
        id=authFid, is_superuser=False, first_name=firstName,
        last_name=lastName, is_staff=False, is_active=True,
        last_login=datetime.datetime.now().replace(microsecond=0),
        date_joined=datetime.datetime.now().replace(microsecond=0)
    )

