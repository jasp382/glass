"""
AUTH URLS Routing
"""

from django.urls import path

from authapi.views      import GetTokens
from authapi.views.gp   import GroupsManage, GroupManage
from authapi.views.us   import ManUsers, CreateJustAUser, ManUser
from authapi.views.psw  import PasswordRecovery, RqstPassRecovery
from authapi.views.attr import ManUserAttr, ManUserAttrs
from authapi.views.org  import ManOrgs, ManOrg

urlpatterns = [
    # Access Tokens
    path('token/<str:op>/', GetTokens.as_view(), name='get-token'),

    # Groups
    path('groups/', GroupsManage.as_view(), name='manage-groups'),
    path('group/<str:gpid>/', GroupManage.as_view(), name='manage-group'),

    # Organizations
    path('org/', ManOrgs.as_view(), name='manage-organizations'),
    path('org/<str:slug>/', ManOrg.as_view(), name='manage-organization'),

    # Users
    path('users/', ManUsers.as_view(), name='manage-users'),
    path('user/<str:userid>/', ManUser.as_view(), name='manage-user'),
    path('justauser/', CreateJustAUser.as_view(), name='create-justauser'),

    path(
        'request-pass-recovery/',
        RqstPassRecovery.as_view(),
        name='request-password-recovery'
    ),

    path(
        'pass-recovery/', PasswordRecovery.as_view(),
        name='password-recovery'
    ),

    # Users Attributes
    path('attrs/', ManUserAttrs.as_view(), name='manage-user-attrs'),
    path(
        'attr/<str:slug>/', ManUserAttr.as_view(),
        name='manage-user-attr'
    ),

    #path('reset/<str:token>/', ResetPassword.as_view(), name='reset-password'),
    #path('reset/', ResetPassword.as_view(), name='reset-password')

    #path('google/', GoogleAuthView.as_view(), name='google-auth'),

    #path('normal/', NormalAuthView.as_view(), name='normal-mail-password-auth')
]