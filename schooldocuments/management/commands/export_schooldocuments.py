from django.core.management.base import BaseCommand
from django.core.files import File
from schooldocuments.models import Admission, Contract
import os
import json
import base64


class Command(BaseCommand):
    help = 'Export schooldocuments data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the output JSON file')

    def handle(self, *args, **options):
        json_file = options['json_file']
        data = []

        # Export Admissions
        for admission in Admission.objects.all():
            admission_data = {
                'model': 'schooldocuments.admission',
                'fields': {
                    'Name': admission.Name,
                    'admission_number': admission.admission_number,
                    'Date_of_Admission': admission.Date_of_Admission.isoformat() if admission.Date_of_Admission else None,
                    'German_Level': admission.German_Level,
                    'pdf_file': self.encode_file(admission.pdf_file) if admission.pdf_file else None,
                }
            }
            data.append(admission_data)

        # Export Contracts
        for contract in Contract.objects.all():
            contract_data = {
                'model': 'schooldocuments.contract',
                'fields': {
                    'candidate': {
                        'First_Name': contract.candidate.First_Name,
                        'Last_Name': contract.candidate.Last_Name,
                        'admission_number': contract.candidate.admission_number,
                    },
                    'signed_contract': self.encode_file(contract.signed_contract) if contract.signed_contract else None,
                }
            }
            data.append(contract_data)

        with open(json_file, 'w') as file:
            json.dump(data, file, indent=2)

        self.stdout.write(self.style.SUCCESS(f'Successfully exported schooldocuments data to {json_file}'))

    def encode_file(self, file_field):
        if file_field and file_field.name:
            try:
                with file_field.open('rb') as f:
                    return {
                        'name': os.path.basename(file_field.name),
                        'content': base64.b64encode(f.read()).decode('utf-8'),
                    }
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"File not found: {file_field.path}"))
                return None
        return None
