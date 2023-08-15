from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate


"""class GoogleAuthView(APIView):
    def post(self, request):

        data = request.data

        if 'email' in data:
            user = authenticate(username=data['email'], password=data['password'])
        
        if 'token' in data:
            user = authenticate(google_token=data['token'])

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            data = {'token': token.key}
            return Response({
            "code"      : "success_google_code",
            "message"   : "successful google authentication",
            "data"      : data,
        }, status=status.HTTP_200_OK)
        else:
            return Response({
            "code"      : "failed_google_code",
            "message"   : "something went wrong with google auth"
        }, status=status.HTTP_400_BAD_REQUEST)
            """