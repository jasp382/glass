# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User

class GoogleAuthView(APIView):
    def post(self, request):

        data = request.data
        token_param = 'idtoken'

        if 'email' in data:
            user = authenticate(username=data['email'], password=data['password'])
        
        if token_param in data:
            user = authenticate(google_token=data[token_param])

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


class NormalAuthView(APIView):
    def post(self, request):

        data = request.data

        if 'email' not in data or 'password' not in data:
            return Response({
                "code"      : "failed_code",
                "message"   : "missing parameters in request body"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=data['email'], password=data['password'])

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            data = {'token': token.key}
            return Response({
                "code"      : "success_auth_code",
                "message"   : "successful email/password authentication",
                "data"      : data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "code"      : "A001",
                "message"   : "user does not exist"
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, post): # stupid endpoint to see users in db

        users = User.objects.all()

        print(users)

        return Response({
            "message"   : "done"
        }, status=status.HTTP_200_OK)


class ResetPassword(APIView): # Don't use in production! Use only for testing if necessary
    
    #get -> validate token
    #put -> send email
     
    def post(self, request):

        data = request.data

        if 'email' not in data or 'password' not in data:
            return Response({
                "code"      : "E01",
                "message"   : "Missing parameters in request body"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=data['email'])

        except (User.DoesNotExist, User.MultipleObjectsReturned) as e:
            print(str(e))
            
            return Response({
                "code"      : "E03",
                "message"   : "User doesn't exist or multiple instances were returned."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user.set_password(data['password'])
        user.save()

        return Response({
            "code"      : "S20",
            "message"   : "Changed the user\'s password successfully"
        }, status=status.HTTP_200_OK)

