from django.core.management.base import BaseCommand
from studentpage.models import Candidate
from qrcodes.models import CandidateQRCode


class Command(BaseCommand):
    help = 'Generates QR codes for all existing candidates'

    def handle(self, *args, **options):
        candidates = Candidate.objects.all()
        for candidate in candidates:
            if not hasattr(candidate, 'qr_code'):
                qr_code = CandidateQRCode.objects.create(candidate=candidate)
                qr_code.generate_qr_code()
                self.stdout.write(self.style.SUCCESS(f'Generated QR code for {candidate.full_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'QR code already exists for {candidate.full_name}'))

        self.stdout.write(self.style.SUCCESS('QR code generation complete'))