from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import SchoolFee


@admin.register(SchoolFee)
class SchoolFeeAdmin(ImportExportModelAdmin):
    list_display = ['candidate', 'starting_month', 'due_date', 'total_amount_to_pay', 'invoice_number']
    list_filter = ['candidate', 'starting_month', 'due_date', 'total_amount_to_pay', 'invoice_number']
    date_hierarchy = 'starting_month'
    list_per_page = 10

