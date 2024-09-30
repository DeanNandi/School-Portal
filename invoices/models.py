from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models


class SchoolFee(models.Model):
    candidate = models.CharField(max_length=255)
    starting_month = models.DateField()
    due_date = models.DateField()
    custom_due_date = models.DateField(null=True, blank=True)
    total_amount_to_pay = models.IntegerField()  # Set fixed amount
    invoice_number = models.CharField(max_length=12)
    has_gap_period = models.BooleanField(default=False)
    gap_period_start_date = models.DateField(null=True, blank=True)
    fee_instance = models.CharField(max_length=255, null=True)
    is_first_month = models.BooleanField(default=False)
    entry_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.candidate} - {self.invoice_number}"

    def get_calculated_due_date(self):
        original_due_date = self.starting_month - timedelta(days=1)
        max_allowed_date = original_due_date + timedelta(weeks=2)

        if self.custom_due_date:
            if self.custom_due_date == self.due_date:
                return original_due_date  # Return original calculated date if custom date equals due_date
            elif self.custom_due_date > max_allowed_date:
                return max_allowed_date  # Return max allowed date if custom date exceeds it
            else:
                return self.custom_due_date

        return original_due_date

    def clean(self):
        super().clean()
        if self.custom_due_date:
            original_due_date = self.starting_month - timedelta(days=1)
            max_allowed_date = original_due_date + timedelta(weeks=2)

            if self.custom_due_date == self.due_date:
                raise ValidationError("Custom due date cannot be equal to the original due date.")

            if self.custom_due_date > max_allowed_date:
                raise ValidationError(
                    "Custom due date cannot be more than two weeks after the original calculated due date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
