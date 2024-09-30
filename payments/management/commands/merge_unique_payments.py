from django.core.management.base import BaseCommand
from payments.models import PaymentRecord, UniquePayment
from django.db.models import Q

class Command(BaseCommand):
    help = 'Merges data from UniquePayment to PaymentRecord for matching receipt_number values.'

    def handle(self, *args, **options):
        # Iterate over UniquePayment records to find matching PaymentRecord by receipt_number
        for unique_payment in UniquePayment.objects.all():
            try:
                payment_record = PaymentRecord.objects.get(receipt_number=unique_payment.receipt_number)
                # Update payment_record with data from unique_payment
                # Assuming other fields like date_of_payment and amount_paid should be updated
                payment_record.date_of_payment = unique_payment.date_of_payment
                payment_record.amount_paid = unique_payment.amount_paid if unique_payment.amount_paid else payment_record.amount_paid
                payment_record.user = unique_payment.user.username if unique_payment.user else payment_record.user
                payment_record.save()
                self.stdout.write(self.style.SUCCESS(f'Updated PaymentRecord {payment_record.receipt_number} with data from UniquePayment.'))
            except PaymentRecord.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'No PaymentRecord found for UniquePayment receipt: {unique_payment.receipt_number}. No action taken.'))
            except PaymentRecord.MultipleObjectsReturned:
                self.stdout.write(self.style.ERROR(f'Multiple PaymentRecords found for receipt: {unique_payment.receipt_number}. Manual review recommended.'))

        self.stdout.write(self.style.SUCCESS('Data merging process completed.'))
