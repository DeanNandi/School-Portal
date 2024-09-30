from django.core.management.base import BaseCommand, CommandError
from studentpage.models import Candidate
from django.db import transaction
import json
from django.db.models.fields.files import FileField, ImageField


class Command(BaseCommand):
    help = 'Import Candidate data from a JSON file, updating existing entries if modified while preserving file fields'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing candidate data')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, 'r') as file:
                candidates_data = json.load(file)
        except FileNotFoundError:
            raise CommandError(f'File "{file_path}" does not exist.')

        total_records = len(candidates_data)
        successful_imports = 0
        successful_updates = 0
        skipped_imports = 0
        failed_imports = 0

        # Get all field names that are file fields
        file_fields = [f.name for f in Candidate._meta.get_fields() if isinstance(f, (FileField, ImageField))]

        for candidate_data in candidates_data:
            try:
                with transaction.atomic():
                    admission_number = candidate_data['fields'].get('admission_number')
                    if not admission_number:
                        self.stdout.write(self.style.ERROR(f'Missing admission number: {candidate_data}'))
                        failed_imports += 1
                        continue

                    # NEW: Handle foreign key fields by converting them to strings
                    for field in ['candidate_type', 'target_level', 'partnership', 'class_schedule']:
                        if field in candidate_data['fields'] and candidate_data['fields'][field] is not None:
                            candidate_data['fields'][field] = str(candidate_data['fields'][field])

                    # Try to find existing candidate by admission number
                    existing_candidate = Candidate.objects.filter(admission_number=admission_number).first()
                    if existing_candidate:
                        # Update existing candidate
                        for field, value in candidate_data['fields'].items():
                            # Exclude admission_number and file fields
                            if field not in ['admission_number'] + file_fields:
                                setattr(existing_candidate, field, value)
                        existing_candidate.save()
                        self.stdout.write(self.style.SUCCESS(f'Updated existing candidate: {existing_candidate}'))
                        successful_updates += 1
                    else:
                        # Create a new Candidate instance
                        new_candidate = Candidate.objects.create(**candidate_data['fields'])
                        self.stdout.write(self.style.SUCCESS(f'Created new candidate: {new_candidate}'))
                        successful_imports += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing candidate: {e}'))
                failed_imports += 1

        # Comprehensive summary
        self.stdout.write('\n' + '-' * 25 + ' Import Summary ' + '-' * 25)
        self.stdout.write(f'Total records in file: {total_records}')
        self.stdout.write(f'Successfully imported (new records): {successful_imports}')
        self.stdout.write(f'Successfully updated: {successful_updates}')
        self.stdout.write(f'Failed to import: {failed_imports}')

        # Additional relevant reports
        self.stdout.write('\nAdditional Details:')
        self.stdout.write(f'Total processed: {successful_imports + successful_updates + failed_imports}')
        self.stdout.write(f'Success rate: {((successful_imports + successful_updates) / total_records) * 100:.2f}%')
        self.stdout.write(f'Failure rate: {(failed_imports / total_records) * 100:.2f}%')
        if failed_imports > 0:
            self.stdout.write(self.style.WARNING('\nWarning: Some imports failed. Please check the logs for details.'))
        self.stdout.write('-' * 25 + ' End of Import Summary ' + '-' * 25 + '\n')
