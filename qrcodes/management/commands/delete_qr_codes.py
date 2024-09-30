from django.core.management.base import BaseCommand
from qrcodes.models import CandidateQRCode


class Command(BaseCommand):
    help = 'Deletes all existing QR codes'

    def handle(self, *args, **options):
        count = CandidateQRCode.objects.count()
        CandidateQRCode.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} QR codes'))
