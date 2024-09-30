# Place this in a management/commands directory within one of your apps
import json
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from payments.models import PaymentRecord  # Update with the correct app name and model


class Command(BaseCommand):
    help = 'Import PaymentRecord data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing PaymentRecord data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r') as file:
                payment_records = json.load(file)

            for record in payment_records:
                try:
                    PaymentRecord.objects.create(
                        candidate_name=record['fields']['candidate_name'],
                        phone_number=record['fields']['phone_number'],
                        receipt_number=record['fields']['receipt_number'],
                        date_of_payment=record['fields']['date_of_payment'],
                        amount_paid=record['fields']['amount_paid'],
                        mode_of_payment=record['fields'].get('mode_of_payment', ''),
                        transaction_details=record['fields'].get('transaction_details', ''),
                    )
                    self.stdout.write(self.style.SUCCESS(f"Imported {record['fields']['receipt_number']} successfully"))
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(f"Skipped duplicate {record['fields']['receipt_number']}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file_path}" does not exist.'))
