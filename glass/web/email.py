"""
E-mail related
"""

def email_exists_old(email):
    """
    Verify if a email exists
    """
    
    from validate_email import validate_email
    
    return validate_email(email, verify=True)


def email_exists(email):
    """
    Verify if a email exists using MailBoxLayer API
    """
    
    from glass.fm.web import http_to_json
    
    API_KEY = "b7bee0fa2b3ceb3408bd8245244b1479"
    
    URL = (
        "http://apilayer.net/api/check?access_key={}&email={}&"
        "smtp=1&format=1"
    ).format(API_KEY, str(email))
    
    jsonArray = http_to_json(URL)
    
    return jsonArray["smtp_check"]

