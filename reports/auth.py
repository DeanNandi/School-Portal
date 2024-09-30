from django.contrib.auth.backends import ModelBackend
from .models import Client


class ClientAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Client.objects.get(username=username)
            if user.check_password(password):
                return user
        except Client.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Client.objects.get(pk=user_id)
        except Client.DoesNotExist:
            return None
