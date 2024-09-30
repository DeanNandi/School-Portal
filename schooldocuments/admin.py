from django.contrib import admin
from .models import Contract, Admission
from django.utils.html import format_html


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('get_candidate_name', 'signed_contract')
    list_filter = ('candidate__First_Name', 'candidate__Last_Name')
    list_per_page = 10

    def get_candidate_name(self, obj):
        return f"{obj.candidate.First_Name} {obj.candidate.Last_Name}"

    get_candidate_name.short_description = 'Student Name'


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('Name', 'admission_number', 'Date_of_Admission', 'pdf_view_link')
    list_filter = ('Name', 'admission_number', 'Date_of_Admission',)
    list_per_page = 10

    def pdf_view_link(self, obj):
        if obj.pdf_file:
            return format_html(f'<a href="{obj.pdf_file.url}" target="_blank">View PDF</a>')
        return "PDF not generated"

    pdf_view_link.short_description = 'PDF Admissions'

    def save_model(self, request, obj, form, change):
        if not change or 'pdf_file' not in form.changed_data:
            # Generate the PDF only if it's a new instance or relevant fields have changed
            obj.create_pdf_for_admissions()

        super().save_model(request, obj, form, change)
