from django.contrib.auth.backends import ModelBackend
from .models import QRScannerUser


class QRScannerAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = QRScannerUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except QRScannerUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return QRScannerUser.objects.get(pk=user_id)
        except QRScannerUser.DoesNotExist:
            return None
