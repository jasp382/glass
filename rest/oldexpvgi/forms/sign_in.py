"""
Login and Registration Forms
"""

from django import forms

class UserRegistration(forms.Form):
    """
    User Registration Form
    """
    
    alphanum = {
        'autocomplete' : 'off', 
        'pattern'      :'[A-Za-z0-9]+',
        'title'        : 'Only alphanumeric characters are allowed'
    }
    
    fname  = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs=alphanum
    ))
    lname  = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs=alphanum
    ))
    user   = forms.CharField(min_length=4, max_length=30, widget=forms.TextInput(
        attrs=alphanum
    ))
    email  = forms.EmailField()
    passw  = forms.CharField(
        widget=forms.PasswordInput, min_length=8, max_length=20)
    repeat = forms.CharField(
        widget=forms.PasswordInput, min_length=8, max_length=20)

