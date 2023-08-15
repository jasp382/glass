from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from google.oauth2 import id_token
from google.auth.transport import requests
from fireapi.settings import GOOGLE
from firebase_admin import credentials, auth, initialize_app

#GOOGLE['CLIENT_ID'] #'773725031158-h3agnrf1t0qaj5ou0ndndqrivd0h23ik.apps.googleusercontent.com'
CLIENT_ID = 'fireloc-testing-firebase-adminsdk-1ei34-de6cb41b79.json'

cred = credentials.Certificate(CLIENT_ID);
firebase_app = initialize_app(cred)

class AuthBackend(BaseBackend):

    def authenticate(self, request, **kwargs):

        if 'email' in kwargs.keys():
            try:
                user = User.objects.get(email=kwargs.get('email'))

                print(str(kwargs) + '--- auth-user->' + str(user))

                if user.check_password(kwargs.get('password')):
                    return user
                else:
                    return None

            except User.DoesNotExist:
                return None

        else:
            return validate_google_token(kwargs.get('google_token'))

    def get_user(self, user_id):
        try:
            return User.objects.get(email=user_id)

        except User.DoesNotExist:
            return None


def validate_google_token(token):
    print('in validate token')
    try:
        decoded_token = auth.verify_id_token(token)

        name = decoded_token['name']
        email = decoded_token['email']

        if not email:
            raise ValueError('No email present in token.')

    except ValueError as e:
        print(str(e))
        return None

    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        print('on does not exist')
        user = User.objects.create(username=email, email=email)
        user.save()
        return user


