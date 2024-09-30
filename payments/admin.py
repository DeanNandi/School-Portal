from django.contrib import admin
from django.db.models import Exists, OuterRef
from .models import PaymentRecord, UniquePayment


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'transaction_details', 'mode_of_payment', 'receipt_number', 'date_of_payment', 'amount_paid', 'user',
                    'exists_in_unique_payments')
    list_filter = ('candidate_name', 'transaction_details', 'mode_of_payment', 'receipt_number', 'user')
    search_fields = ('candidate_name', 'transaction_details', 'receipt_number')
    list_per_page = 10

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            exists_in_unique_payments=Exists(
                UniquePayment.objects.filter(receipt_number=OuterRef('receipt_number'))
            )
        )
        return queryset

    def exists_in_unique_payments(self, obj):
        return obj.exists_in_unique_payments

    exists_in_unique_payments.boolean = True
    exists_in_unique_payments.short_description = 'Exists in Unique Payments?'
    exists_in_unique_payments.admin_order_field = 'exists_in_unique_payments'  # Allows sorting by this field in the admin


@admin.register(UniquePayment)
class UniquePaymentAdmin(admin.ModelAdmin):
    list_display = (
    'candidate', 'receipt_number', 'date_of_payment', 'amount_paid', 'user', 'exists_in_payment_records')
    list_filter = ('candidate', 'receipt_number', 'date_of_payment', 'amount_paid')
    search_fields = ('receipt_number',)
    list_per_page = 10

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            exists_in_payment_records=Exists(
                PaymentRecord.objects.filter(receipt_number=OuterRef('receipt_number'))
            )
        )
        return queryset

    def exists_in_payment_records(self, obj):
        return obj.exists_in_payment_records

    exists_in_payment_records.boolean = True
    exists_in_payment_records.short_description = 'Exists in Payment Records?'
    exists_in_payment_records.admin_order_field = 'exists_in_payment_records'  # Enables sorting by this field
