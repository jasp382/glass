"""
Database Table to HTTP Response
"""


def tbl_to_http(request, dtype, table):
    """
    Parse any type of data in the database to a Json Response
    
    Query parameters as GET Parameters
    """
    
    from django.http import HttpResponse
    from glass.webg.djg.mdl.serial import serialize_by_getParam
    
    data = serialize_by_getParam(request, dtype, table)
    
    return HttpResponse(data, content_type='json')


def tbl_to_http_filter(request, dtype, table, field, value, typevalue):
    """
    Return objects with a certain value in an certain column
    
    Use only if value is numerical
    """
    
    from django.http import HttpResponse
    from glass.webg.djg.mdl.serial import tbl_serialize
    
    __val = "'{}'".format(value) if typevalue == 'str' else value
    """
    data = serialize_by_query(
        table, "SELECT * FROM {} WHERE {}={}".format(
            table, field, __val
        ), dtype
    )"""
    data = tbl_serialize(table, dtype, filterQ={field: value})
    
    return HttpResponse(data, content_type='json')


def tbl_to_http_join(request, dtype, table, fid,
                join_table, join_fid, interest_field,
                value):
    """
    Parse data on the database to a Json Response
    
    Query parameters are in the request url:
    * dtype      - json (raw json) or gjson (GeoJson)
    * table      - name of the table with the data
    * fid        - primary key of 'table'
    * join_table - name of the table to be joined to the first
    * join_fid   - foreign key in 'join_table'
    * interest_field - Field to be used in the WHERE CLAUSE
    * value      - value of the interest field to be selected
    
    With this execute a query as:
    SELECT * FROM table INNER JOIN join_table ON
    table.join_fid = join_table.join_fid
    WHERE interest_field=value
    
    LIMITATION: it allows only one field and value in the WHERE CLAUSE
    """
    
    from django.http import HttpResponse
    from glass.webg.djg.mdl.serial import serialize_by_query
    
    obj_of_int = '\'{}\''.format(str(
        value)) if type(value) == str else str(value)
    
    QUERY = (
        'SELECT * FROM {tbl} INNER JOIN {jntbl} ON '
        '{tbl}.{fld_tbl} = {jntbl}.{fld_jntbl} '
        'WHERE {fld}={val};'
    ).format(
        tbl=table, jntbl=join_table,
        fld_tbl=fid, fld_jntbl=join_fid,
        fld=interest_field, val=obj_of_int
    )
    
    data = serialize_by_query(table, QUERY, dtype)
    
    return HttpResponse(data, content_type='json')


def del_dt_tbl(request, appname, table):
    """
    Delete data in table
    """
    
    from django.http import HttpResponse
    from glass.pys   import __import
    
    mdl = __import('{}.models.{}'.format(appname, table))
    
    mdl.objects.all().delete()
    
    return HttpResponse('{}_{} is now without data!'.format(appname, table))

