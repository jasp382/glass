"""
Filter data from Django Models
"""


def get_model_obj_by_query(model, query):
    """
    Return Model objects using a raw query
    """
    
    from glass.pys import __import
    
    # Get Model Object
    app_model = model.split('_')
    modelObj = __import('{}.models.{}'.format(
        app_model[0], '_'.join(app_model[1:])
    ))
    
    out = modelObj.objects.raw(query)
    
    return out

