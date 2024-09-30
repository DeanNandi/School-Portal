import json
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from payments.models import UniquePayment


class Command(BaseCommand):
    help = 'Import UniquePayment data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing UniquePayment data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r') as file:
                payments_data = json.load(file)

            successful_imports = 0
            skipped_imports = 0

            with transaction.atomic():
                for record in payments_data:
                    # Check if a payment with the same receipt_number already exists
                    receipt_number = record['receipt_number']
                    if UniquePayment.objects.filter(receipt_number=receipt_number).exists():
                        skipped_imports += 1
                        self.stdout.write(self.style.WARNING(f"Receipt {receipt_number} already exists. Skipping."))
                        continue  # Skip this record if it already exists

                    UniquePayment.objects.create(
                        candidate=record['candidate'],  # Candidate's name
                        user=record['user'],  # User's identifier
                        receipt_number=receipt_number,
                        date_of_payment=record['date_of_payment'],
                        amount_paid=record['amount_paid'],
                    )
                    successful_imports += 1

            self.stdout.write(
                self.style.SUCCESS(f"Completed import: {successful_imports} successful, {skipped_imports} skipped."))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file_path}" does not exist.'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Error decoding JSON. Please check the file format.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
