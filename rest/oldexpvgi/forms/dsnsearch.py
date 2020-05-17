"""
Forms for vgi app
"""

from django import forms

class SearchForPosts(forms.Form):
    
    keyword = forms.CharField(
        label='Enter what you want to get', max_length=100,
        required=False
    )
    
    data_sources = forms.CharField()
    
    draw_circle = forms.CharField()

