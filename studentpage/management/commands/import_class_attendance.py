from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from studentpage.models import Candidate
from attendancepage.models import ClassAttendance
import json


class Command(BaseCommand):
    help = 'Import and update Class Attendance data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing class attendance data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r') as file:
                attendance_data = json.load(file)
        except FileNotFoundError:
            raise CommandError(f'File "{file_path}" does not exist.')

        successful_imports = 0
        missing_candidates = []

        for item in attendance_data:
            fields = item.get('fields', {})
            admission_number = fields.get('candidate_admission_number')

            if not admission_number:
                self.stdout.write(self.style.ERROR('Missing candidate admission number in an attendance record.'))
                continue

            try:
                with transaction.atomic():
                    candidate = Candidate.objects.filter(admission_number=admission_number).first()
                    if not candidate:
                        self.stdout.write(
                            self.style.ERROR(f'Candidate with admission number {admission_number} does not exist.'))
                        missing_candidates.append(admission_number)
                        continue

                    attendance, _ = ClassAttendance.objects.update_or_create(
                        pk=item.get('pk'),
                        defaults={
                            'candidate': candidate,
                            'date': fields.get('date'),
                            'present': fields.get('present'),
                            'absent_reason': fields.get('absent_reason', ''),
                        }
                    )
                    successful_imports += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing attendance data: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully processed {successful_imports} class attendance records.'))
        if missing_candidates:
            self.stdout.write(
                self.style.ERROR(f'Failed to find candidates for admission numbers: {", ".join(missing_candidates)}'))
