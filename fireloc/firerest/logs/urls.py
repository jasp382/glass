"""
Logging check URLS
"""

from django.urls import path

from logs.views import LogsList

urlpatterns = [
    path('<str:app>/', LogsList.as_view(), name='list-logs')
]