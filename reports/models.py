from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.contrib.auth.hashers import make_password, check_password


class Client(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    is_locked_out = models.BooleanField(default=False)
    lockout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s activity"

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.is_locked_out = False
        self.lockout_time = None
        self.save()

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= 5:
            self.is_locked_out = True
            self.lockout_time = timezone.now()
        self.save()


class PaymentIdentification(models.Model):
    description = models.CharField(max_length=1000, blank=True, null=True)
    money_in = models.CharField(max_length=500, blank=True, null=True)
