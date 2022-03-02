"""
Deal with Users registration and Log in
"""

from django.http               import HttpResponseRedirect
from django.shortcuts          import render
from django.contrib.auth       import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    """
    LogIn View
    """
    
    from interface.forms.sign_in import UserRegistration
    
    SERVICE_META = {'name' : 'login', 'about' : 'vgi-login', 'url' : '/expvgi/'}
    
    if request.method == 'POST':
        """
        Check if login is valid
        """
        
        username = request.POST['username']
        password = request.POST['password']
        next_url = request.POST['next']
        
        user = authenticate(
            request, username=username,
            password=password
        )
        
        if user is not None:
            login(request, user)
            
            return HttpResponseRedirect(next_url)
        
        else:
            return render(request, 'login.html', {
                'form'        : AuthenticationForm(),
                'regform'     : UserRegistration(),
                'next'        : next_url,
                'login_error' : 'verdade',
                'service'     : SERVICE_META
            })
    
    else:
        next    = request.GET['next'] if 'next' in request.GET else '/expvgi/'
        newUser = 1 if 'newuser' in request.GET else 0
        
        return render(request, 'login.html', {
            'form'        : AuthenticationForm(),
            'regform'     : UserRegistration(),
            'next'        : next,
            'login_error' : 'mentira',
            'service'     : SERVICE_META,
            'isnewuser'   : newUser
        })


def register(request):
    if request.method == 'POST':
        from gui.settings     import DATABASES
        from django.http      import HttpResponse
        from gasp.web.djg.usr import add_new_user
        from gasp.web.email   import email_exists
        from gasp.sql.fm      import q_to_obj
        
        # Check if FORM parameters are correctly defined
        notCorr = None
        for param in request.POST:
            if request.POST[param] == '':
                notCorr    = 1
                errorParam = param
                break
        
        if notCorr:
            # Parameters are not valid
            return HttpResponseRedirect("/expvgi/error/log/ll/{}/".format(
                "empty_{}".format(errorParam)
            ))
        
        if request.POST["passw"] != request.POST["repeat"]:
            # Passwords are not valid
            # Return an error
            return HttpResponseRedirect("/expvgi/error/log/ll/passw/")
        
        # See if username already exists
        CON_PG = {
            "HOST"     : DATABASES['default']['HOST'],
            "USER"     : DATABASES['default']['USER'],
            "PORT"     : DATABASES['default']['PORT'],
            "PASSWORD" : DATABASES['default']['PASSWORD'],
            "DATABASE" : DATABASES['default']['DATABASE']
        }
        users = q_to_obj(CON_PG,
            "SELECT username, email FROM public.auth_user ORDER BY id"
        )
        
        userIsValid = users.username.str.contains(
            str(request.POST['user'])).any()
        
        if userIsValid:
            # Username already exists
            return HttpResponseRedirect("/expvgi/error/log/ll/repeat_user/")
        
        # See if email exists and if it is unique
        emailExists = users.email.str.contains(
            str(request.POST['email'])).any()
        
        if emailExists:
            # Email already exists
            return HttpResponseRedirect("/expvgi/error/log/ll/repeat_email/")
        
        emailIsValid = email_exists(str(request.POST["email"]))
        
        if not emailIsValid:
            # Email does not exist
            return HttpResponseRedirect("/expvgi/error/log/ll/emailnot/")
        
        # No problems were recorded - Add new user to database        
        add_new_user(
            request.POST["user"],
            request.POST["fname"], request.POST["lname"],
            request.POST["email"], request.POST["passw"]
        )
        
        return HttpResponseRedirect('/expvgi/login/?newuser=1')
    else:
        return HttpResponseRedirect('/expvgi/login/')


def error_login(request, error_descript):
    """
    Return error on login or User registration
    """
    
    SERVICE_META = {'name' : 'login', 'about' : 'vgi-login', 'url' : '/expvgi/'}
    
    # Get Error Description:
    if error_descript == 'empty_fname':
        errorStr = (
            'First Name Parameter is empty. Please give a valid First Name.'
        )
    
    elif error_descript == 'empty_lname':
        errorStr = (
            'Last Name Parameter is empty. Please give a valid Last Name.'
        )
    
    elif error_descript == 'empty_email':
        errorStr = (
            'E-mail Parameter is empty. Please give us a valid E-mail.'
        )
    
    elif error_descript == 'empty_user':
        errorStr = (
            "Username Parameter is empty. Please give us a valid Username."
        )
    
    elif error_descript == 'empty_pass':
        errorStr = (
            "Password Parameter is empty. Please provide a valid Password."
        )
    
    elif error_descript == 'empty_repeat':
        errorStr = (
            "Repeat Password Parameter is empty. "
            "Please repeat password."
        )
    
    elif error_descript == 'passw':
        errorStr = (
            'The provided passwords are not matched. '
            'Password and Repeat Password must be the same.'
        )
    
    elif error_descript == 'emailnot':
        errorStr = (
            'The E-mail you provided does not exist. '
            'Please give us a valid E-mail.'
        )
    
    elif error_descript == 'char_fname':
        errorStr = (
            'First Name Parameter can not be longer than 30 '
            'characters. Please give a valid First Name.'
        )
    
    elif error_descript == 'char_lname':
        errorStr = (
            'Last Name Parameter can not be longer than 30 '
            'characters. Please give a valid Last Name.'
        )
    
    elif error_descript == 'char_user':
        errorStr = (
            'Username Parameter can not be longer than 30 '
            'characters. Please provide a valid Username.'
        )
    
    elif error_descript == 'char_pass':
        errorStr = (
            'Password Parameter can not be longer than 20 '
            'characters. Please provide a valid Password.'
        )
    
    elif error_descript == 'repeat_user':
        errorStr = (
            'Username provided already exists. Please '
            'choose an alternate username.'
        )
    
    elif error_descript == 'repeat_email':
        errorStr = (
            'E-mail provided already exists in our Database. '
            'Please give us a valid E-mail.'
        )
    
    else:
        errorStr = 'Unknow error'
    
    return render(request, 'error_login.html', {
        "error" : errorStr,
        "service" : SERVICE_META
    })

