from django.db import models


class PaymentRecord(models.Model):
    candidate_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    receipt_number = models.CharField(max_length=12, unique=True)
    date_of_payment = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    mode_of_payment = models.CharField(max_length=255, null=True, blank=True)
    transaction_details = models.CharField(max_length=255, null=True, blank=True)
    user = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.candidate_name} - Receipt: {self.receipt_number}"


class UniquePayment(models.Model):
    candidate = models.CharField(max_length=255, null=True, blank=True)
    receipt_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    date_of_payment = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    user = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.date_of_payment} - Receipt: {self.receipt_number}"

# Ensure this model is either completely commented out or set as managed = False and not used in any view or admin

# class PaymentComparison(models.Model):
#     payment_record = models.OneToOneField(PaymentRecord, on_delete=models.CASCADE, primary_key=True)
#     is_unique = models.BooleanField(default=False)
#
#     class Meta:
#         managed = False  # Ensure no database table is created or managed
#
#     def __str__(self):
#         return f"{self.payment_record.receipt_number} - Unique: {self.is_unique}"
#
#     @property
#     def is_unique(self):
#         return not UniquePayment.objects.filter(receipt_number=self.payment_record.receipt_number).exists()
