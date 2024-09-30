from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
import json
import base64
import os
from studentpage.models import Candidate


class Command(BaseCommand):
    help = 'Export Candidate file data to JSON file for Agcrm import'

    def add_arguments(self, parser):
        parser.add_argument('output_file', type=str, help='Path to the output JSON file')

    def handle(self, *args, **options):
        output_file = options['output_file']
        candidates = Candidate.objects.all()
        data = []

        file_fields = [
            'Birth_certificate', 'photo', 'certificate_of_good_conduct', 'passport',
            'english_file', 'german_file', 'Licence_file', 'Nursing_Certificate',
            'High_School_file', 'University_file', 'University_secondary_file',
            'University_tertiary_file', 'College_Degree_file', 'College_Degree_secondary_file',
            'College_tertiary_file', 'Institution_file', 'Institution_file_secondary',
            'Institution_file_tertiary', 'resume_file', 'identification_card_file'
        ]

        for candidate in candidates:
            if not candidate.admission_number:
                self.stdout.write(self.style.WARNING(
                    f'Skipping candidate {candidate.First_Name} {candidate.Last_Name} - No admission number'))
                continue

            candidate_data = {
                'admission_number': candidate.admission_number,
                'First_Name': candidate.First_Name,
                'Last_Name': candidate.Last_Name,
                'files': {}
            }

            for field in file_fields:
                file = getattr(candidate, field)
                if file:
                    try:
                        if not os.path.exists(file.path):
                            raise FileNotFoundError
                        with file.open('rb') as f:
                            file_content = f.read()
                            encoded_content = base64.b64encode(file_content).decode('utf-8')
                            candidate_data['files'][field] = {
                                'name': file.name,
                                'content': encoded_content
                            }
                    except (FileNotFoundError, ObjectDoesNotExist):
                        self.stdout.write(self.style.WARNING(
                            f'File not found for {candidate.First_Name} {candidate.Last_Name}, field: {field}'))

            data.append(candidate_data)

        with open(output_file, 'w') as file:
            json.dump(data, file)

        self.stdout.write(self.style.SUCCESS(f'Successfully exported Candidate file data to {output_file}'))
