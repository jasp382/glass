"""
Django utils for Seralization
"""


def tbl_serialize(model, dataType, filterQ=None):
    """
    Serialize Data in Database Table
    """
    
    from django.core.serializers import serialize
    from glass.pyt import __import
    
    app_mdl = model.split('_')
    app, mdl = app_mdl[0], '_'.join(app_mdl[1:])
    djgMdl = __import('{}.models.{}'.format(app, mdl))
    
    dataType = 'geojson' if dataType == 'gjson' or dataType == 'geojson' \
        else 'json'
    
    if filterQ:
        data = serialize(dataType, djgMdl.objects.filter(**filterQ))
    else:
        data = serialize(dataType, djgMdl.objects.all())
    
    return data


def serialize_by_getParam(request, dtype, table):
    """
    Parse any type of data from the Django Database to a Json Object
    """
    
    from django.core.serializers import serialize
    
    from glass.pyt           import __import
    from glass.web.djg.mdl.i import get_fieldsTypes
    
    def __getWhrTemplate(t):
        return '{}=\'{}\'' if t == str else '{}={}'
    
    appAndModel = table.split('_')
    django_model = __import('{}.models.{}'.format(
        appAndModel[0], '_'.join(appAndModel[1:])
    ))
    
    dataTag = 'geojson' if dtype == 'gjson' or dtype == 'geojson' \
        else 'json'
    
    # Get Columns name and type
    colsTypes = get_fieldsTypes(django_model)
    colsName  = set(colsTypes.keys())
    colsGET   = set([str(x) for x in request.GET.keys()])
    colsQuery = list(colsName.intersection(colsGET))
    
    if any(colsQuery):
        # Do a query
        dicQuery = {}
        fldCount = 0
        
        for fld in request.GET.keys():
            if fld != 'logic':
                dicQuery[fld] = request.GET[fld].split('_')
                fldCount += 1
        
        if fldCount and fldCount == 1:
            field = list(dicQuery.keys())[0]
            fld_type = colsTypes[field]
            
            fld_value_template = __getWhrTemplate(fld_type)
            
            whr = ' OR '.join([
                fld_value_template.format(field, v) for v in dicQuery[field]
            ])
        
        elif fldCount and fldCount > 1:
            logic = 'OR' if 'logic' not in request.GET else \
                request.GET['logic']
            
            for field in dicQuery:
                fld_type = colsTypes[field]
                
                fld_value_template = __getWhrTemplate(fld_type)
                
                docQuery[field] = ' OR '.join([
                    fld_value_template.format(
                        field, x) for x in dicQuery[field]
                ])
            
            __logic = ' {} '.format(logic)
            whr = __logic.join([
                '({})'.format(dicQuery[k]) for k in dicQuery.keys()
            ])
        
        __data = serialize(dataTag, django_model.objects.raw(
            'SELECT * FROM {} WHERE {}'.format(table, whr)
        ))
    
    else:
        __data = serialize(dataTag, django_model.objects.all())
    
    return __data


def serialize_by_query(model, query, dataType):
    """
    Return data extracted from the Django Database using Raw SQL
    Query
    """
    
    from django.core.serializers import serialize
    from glass                    import __import
    
    appAndModel = model.split('_')
    djgModel = __import('{}.models.{}'.format(
        appAndModel[0], '_'.join(appAndModel[1:])
    ))
    
    dataType = 'geojson' if dataType == 'gjson' or dataType=='geojson' \
         else 'json'
    
    data = serialize(dataType, djgModel.objects.raw(query))
    
    return data


def mdl_serialize_to_json(model, dataType, filePath, filterQ=None):
    """
    Serialize data from Django Database and store it in one file
    """
    
    from django.core.serializers import get_serializer
    from glass import __import
    
    # Get Model object
    app_model = model.split('_')
    modelObj = __import('{}.models.{}'.format(
        app_model[0], '_'.join(app_model[1:])
    ))
    
    # Get Serializer for json
    JSON_Serializer = get_serializer(dataType)
    json_serializer = JSON_Serializer()
    
    # Write file with data
    with open(filePath, "w") as out:
        json_serializer.serialize(
            modelObj.objects.all() if not filterQ else modelObj.objects.filter(
                **filterQ
            ),
            stream=out
        )

