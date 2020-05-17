"""
Info about Django Models
"""

def get_special_tables():
    return {
        'auth_user'        : 'django.contrib.auth.models.User',
        'auth_group'       : 'django.contrib.auth.models.Group',
        'auth_user_groups' : ''
    }


def get_ignore_tables():
    return [
        'django_Permission',
        'django_Group',
        'django_LogEntry'
    ]


def list_fieldsName(model_obj):
    """
    List fields in Model
    """
    
    fields = model_obj._meta.get_fields()
    
    fld_name = [fld.name for fld in fields]
    
    return fld_name


def get_fieldsTypes(model_obj):
    """
    get type of the lifes in on django model
    """
    
    fields = model_obj._meta.get_fields()
    
    flds = {}
    for field in fields:
        t = field.get_internal_type()
        
        if t == 'AutoField' or t == 'IntegerField' or \
            t == 'BigAutoField' or t == 'BigIntegerField':
            flds[field.name] = int
        
        elif t == 'CharField':
            flds[field.name] = str
        
        elif t == 'BooleanField' or t == 'ForeignKey' or \
            t == 'PolygonField' or t == 'DateField':
            continue
        else:
            continue
    
    return flds


def isForeign_key_in_model(mdl, exportAllFields=None, specialModel=None):
    """
    There is any foreign key in one model
    """
    
    from django.contrib.gis.db import models
    from glass.pyt import __import
    
    # List fields in model
    if mdl and specialModel:
        raise ValueError(
            'Please define modelName/AppName or only specialModel'
        )
    
    if mdl:
        modelObj = __import(mdl)
    
    elif specialModel:
        modelObj = __import(get_special_tables()[specialModel])
    
    else:
        raise ValueError((
            'Nothing to do... '
            'Please define modelName/AppName or only specialModel'
        ))
    
    fields = list_fieldsName(modelObj)
    
    # Check if the field is a foreign key
    fk_fields = []
    for field in fields:
        fieldObj = modelObj._meta.get_field(field)
        if isinstance(fieldObj, models.ForeignKey):
            fk_fields.append(field)
    
    return fk_fields if not exportAllFields else \
           (fk_fields, fields)


def lst_mdl_no_fk(tables, proj_path=None):
    """
    List tables without foreign keys
    """
    
    if proj_path:
        from glass.web.djg import open_Django_Proj
        
        application = open_Django_Proj(proj_path)
    
    result = []
    for mdl in tables:
        fk_fields = isForeign_key_in_model(mdl)
        
        if fk_fields:
            continue
        else:
            result.append(mdl)
    
    return result


def lst_mdl_proj(path, thereIsApp=None, returnClassName=None):
    """
    List Django Models in Project
    """
    
    if not thereIsApp:
        from glass.web.djg import open_Django_Proj
        
        application = open_Django_Proj(path)
    
    from glass.web.djg.i import list_djg_apps
    
    lst_apps = list_djg_apps(path)
    
    from django.apps import apps
    
    mdls = [] if not returnClassName else {}
    for __app in lst_apps:
        mdl = apps.get_app_config(__app).models
        
        if not returnClassName:
            mdls += ["{}_{}".format(__app, k) for k in mdl]
        else:
            for k in mdl:
                mdls["{}_{}".format(__app, k)] = mdl[k].__name__
    
    return mdls

