
"""
Utilies for the application
"""

from rest_framework.views import exception_handler

def custom_exception(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        if response.data['detail'] == "Authentication credentials were not provided.":
            response.data["status"] = {
                'code'    : 'A02',
                'message' : "Token was not provided or it is invalid!"
            }
        
        elif response.data['detail'] == "You do not have permission to perform this action.":
            response.data["status"] = {
                'code'    : 'E03',
                'message' : response.data['detail']
            }

        elif response.data['detail'] == "Invalid username/password.":
            response.data["status"] = {
                'code'    : 'A01',
                'message' : response.data['detail']
            }
        
        elif response.data['detail'] == "Method \"GET\" not allowed.":
            response.data["status"] = {
                'code'    : 'E04',
                'message' : response.data['detail']
            }
        
        elif response.data['detail'] == "Method \"DELETE\" not allowed.":
            response.data["status"] = {
                'code'    : 'E04',
                'message' : response.data['detail']
            }
        
        elif response.data['detail'] == "Method \"PUT\" not allowed.":
            response.data["status"] = {
                'code'    : 'E04',
                'message' : response.data['detail']
            }
        
        elif response.data['detail'] == "Method \"POST\" not allowed.":
            response.data["status"] = {
                'code'    : 'E04',
                'message' : response.data['detail']
            }
        
        elif response.data['detail'] == "JSON parse error - Expecting value: line 1 column 1 (char 0)":
            response.data["status"] = {
                'code'    : 'E05',
                'message' : "POST data is not in JSON format"
            }
        
        else:
            response.data["status"] = {
                'code'    : 'UNK',
                'message' : response.data['detail']
            }
        
        del response.data["detail"]
    
    return response

