from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from studentpage.models import Candidate
from schooldocuments.models import Admission, Contract
import json


class Command(BaseCommand):
    help = 'Import schooldocuments data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = options['json_file']

        with open(json_file, 'r') as file:
            data = json.load(file)

        for obj_data in data:
            if obj_data['model'] == 'schooldocuments.admission':
                self.import_admission(obj_data)
            elif obj_data['model'] == 'schooldocuments.contract':
                self.import_contract(obj_data)

        self.stdout.write(self.style.SUCCESS('Successfully imported schooldocuments data'))

    def import_admission(self, obj_data):
        admission_data = obj_data['fields']
        Admission.objects.create(**admission_data)

    def import_contract(self, obj_data):
        contract_data = obj_data['fields']
        candidate_data = contract_data.pop('candidate')
        candidate = Candidate.objects.get(
            First_Name=candidate_data['First_Name'],
            Last_Name=candidate_data['Last_Name']
        )
        Contract.objects.create(candidate=candidate, **contract_data)
