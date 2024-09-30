from django.db import models
from django.urls import reverse
from studentpage.models import Candidate
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings

# Authentication for scanning
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class QRScannerUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class QRScannerUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = QRScannerUserManager()

    USERNAME_FIELD = 'username'

    # Add these lines to resolve the conflict
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='qrscanner_users',  # Add this line
        related_query_name='qrscanner_user',  # Add this line
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='qrscanner_users_permissions',  # Add this line
        related_query_name='qrscanner_user_permission',  # Add this line
    )

    def __str__(self):
        return self.username


# end authentication models
class CandidateQRCode(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='qr_code')
    qr_code = models.ImageField(upload_to='candidate_qr_codes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_scanned = models.DateTimeField(null=True, blank=True)
    scan_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"QR Code for {self.candidate.full_name}"

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        scan_url = reverse('scan_qr_code', args=[self.candidate.id])
        full_url = f"{settings.BASE_URL}{scan_url}"
        qr.add_data(full_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_code_{self.candidate.id}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        self.save()


@receiver(post_save, sender=Candidate)
def create_qr_code(sender, instance, created, **kwargs):
    if created:
        qr_code = CandidateQRCode.objects.create(candidate=instance)
        qr_code.generate_qr_code()


class QRCodeScan(models.Model):
    qr_code = models.ForeignKey(CandidateQRCode, on_delete=models.CASCADE, related_name='scans')
    scanned_at = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=50, choices=Candidate.COURSE_LOCATION, null=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Scan of {self.qr_code.candidate.full_name}'s QR code at {self.scanned_at}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.qr_code.last_scanned = self.scanned_at
        self.qr_code.scan_count += 1
        self.qr_code.save()

    @property
    def candidate(self):
        return self.qr_code.candidate
