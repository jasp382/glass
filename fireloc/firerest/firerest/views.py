"""
Index View
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework import status

from firerest.settings import ADMIN_URL

class IndexView(APIView):
    """
    Run index view
    """

    def get(self, request, format=None):
        return Response({
            "api"       : "firerest",
            "project"   : "FireLoc",
            "version"   : "0.0.2"
        }, status=status.HTTP_200_OK)



def admin_redirect(request):
    return HttpResponseRedirect(f'/{ADMIN_URL}/admin/')

