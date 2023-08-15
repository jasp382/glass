"""
Some utilities
"""



def id_usertype(user):
    """
    Return user type
    """

    if user.is_superuser:
        return 'superuser'
    
    if user.groups.filter(name='fireloc').exists():
        utype = 'fireloc'
    
    elif user.groups.filter(name='riskmanager').exists():
        utype = 'riskmanager'
        
    else:
        utype = 'justauser'
    
    return utype

