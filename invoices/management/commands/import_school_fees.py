import json
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from invoices.models import SchoolFee


class Command(BaseCommand):
    help = 'Import SchoolFee data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file containing SchoolFee data')

    def handle(self, *args, **options):
        file_path = options['file_path']
        successful_imports = 0
        skipped_existing = 0
        failed_imports = 0
        total_records = 0

        try:
            with open(file_path, 'r') as file:
                fees_data = json.load(file)

            total_records = len(fees_data)

            for record in fees_data:
                invoice_number = record['fields']['invoice_number']

                # Check if a record with the same invoice_number already exists
                if SchoolFee.objects.filter(invoice_number=invoice_number).exists():
                    skipped_existing += 1
                    self.stdout.write(self.style.WARNING(f"Invoice {invoice_number} already exists. Skipping."))
                    continue  # Skip to the next record

                try:
                    SchoolFee.objects.create(
                        candidate=f"{record['fields']['candidate']['First_Name']} {record['fields']['candidate']['Last_Name']}",
                        starting_month=record['fields']['starting_month'],
                        due_date=record['fields']['due_date'],
                        custom_due_date=record['fields'].get('custom_due_date'),
                        total_amount_to_pay=record['fields']['total_amount_to_pay'],
                        invoice_number=invoice_number,
                        has_gap_period=record['fields'].get('has_gap_period', False),
                        gap_period_start_date=record['fields'].get('gap_period_start_date'),
                        fee_instance=str(record['fields'].get('fee_instance')),
                        is_first_month=record['fields'].get('is_first_month', False),
                        entry_order=record['fields'].get('entry_order', 0)
                    )
                    successful_imports += 1
                    self.stdout.write(self.style.SUCCESS(f"Imported invoice {invoice_number} successfully"))
                except IntegrityError as e:
                    failed_imports += 1
                    self.stdout.write(self.style.ERROR(f"Failed to import {invoice_number}: {str(e)}"))
                except Exception as e:
                    failed_imports += 1
                    self.stdout.write(self.style.ERROR(f"Unexpected error importing {invoice_number}: {str(e)}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File "{file_path}" does not exist.'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Invalid JSON format in file "{file_path}".'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {str(e)}'))

        # Output summary of the import operation
        self.stdout.write("\n--- Import Summary ---")
        self.stdout.write(f"Total records in file: {total_records}")
        self.stdout.write(self.style.SUCCESS(f"Successfully imported: {successful_imports}"))
        self.stdout.write(self.style.WARNING(f"Skipped (already existing): {skipped_existing}"))
        self.stdout.write(self.style.ERROR(f"Failed to import: {failed_imports}"))

        total_processed = successful_imports + skipped_existing + failed_imports
        if total_processed != total_records:
            self.stdout.write(self.style.WARNING(
                f"Warning: Total processed records ({total_processed}) doesn't match total records in file ({total_records})"))

        self.stdout.write("--- End of Import Summary ---")
