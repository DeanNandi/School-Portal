from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CandidateQRCode, QRCodeScan
# Authentication for users
from .models import QRScannerUser


@admin.register(QRScannerUser)
class QRScannerUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_active', 'is_staff', 'is_superuser', 'last_login')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username',)
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(CandidateQRCode)
class CandidateQRCodeAdmin(admin.ModelAdmin):
    list_display = (
    'get_full_name', 'get_admission_number', 'created_at', 'last_scanned', 'scan_count', 'display_qr_code',
    'view_candidate')
    list_filter = ('created_at', 'last_scanned', 'candidate__Course_Location', 'candidate__Time')
    search_fields = (
    'candidate__First_Name', 'candidate__Last_Name', 'candidate__admission_number', 'candidate__email_address')
    readonly_fields = ('created_at', 'last_scanned', 'scan_count', 'display_qr_code')

    fieldsets = (
        ('Candidate Information', {
            'fields': ('candidate', 'created_at')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'display_qr_code')
        }),
        ('Scan Information', {
            'fields': ('last_scanned', 'scan_count')
        }),
    )

    def get_full_name(self, obj):
        return obj.candidate.full_name

    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'candidate__First_Name'

    def get_admission_number(self, obj):
        return obj.candidate.admission_number

    get_admission_number.short_description = 'Admission Number'
    get_admission_number.admin_order_field = 'candidate__admission_number'

    def display_qr_code(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="150" height="150" />')
        return "No QR Code"

    display_qr_code.short_description = 'QR Code'

    def view_candidate(self, obj):
        url = reverse("admin:studentpage_candidate_change", args=[obj.candidate.id])
        return format_html('<a href="{}">View Candidate</a>', url)

    view_candidate.short_description = "Candidate Details"

    actions = ['generate_candidate_report']

    def generate_candidate_report(self, request, queryset):
        total_candidates = queryset.count()
        total_scans = sum(obj.scan_count for obj in queryset)
        avg_scans = total_scans / total_candidates if total_candidates > 0 else 0
        most_scanned_candidate = queryset.order_by('-scan_count').first()

        message = f"Total Candidates: {total_candidates}<br>"
        message += f"Total Scans: {total_scans}<br>"
        message += f"Average Scans per Candidate: {avg_scans:.2f}<br>"
        if most_scanned_candidate:
            message += f"Most Scanned Candidate: {most_scanned_candidate.candidate.full_name} ({most_scanned_candidate.scan_count} scans)<br>"

        self.message_user(request, mark_safe(message))

    generate_candidate_report.short_description = "Generate Candidate Report"


@admin.register(QRCodeScan)
class QRCodeScanAdmin(admin.ModelAdmin):
    list_display = ('get_candidate_name', 'get_admission_number', 'scanned_at', 'location')
    list_filter = ('scanned_at', 'location', 'qr_code__candidate__Course_Location', 'qr_code__candidate__Time')
    search_fields = (
    'qr_code__candidate__First_Name', 'qr_code__candidate__Last_Name', 'qr_code__candidate__admission_number',
    'qr_code__candidate__email_address', 'location')
    date_hierarchy = 'scanned_at'

    fieldsets = (
        ('Scan Information', {
            'fields': ('qr_code', 'scanned_at', 'location')
        }),
        ('Additional Information', {
            'fields': ('additional_info',)
        }),
    )

    def get_candidate_name(self, obj):
        return obj.qr_code.candidate.full_name

    get_candidate_name.short_description = 'Candidate Name'
    get_candidate_name.admin_order_field = 'qr_code__candidate__First_Name'

    def get_admission_number(self, obj):
        return obj.qr_code.candidate.admission_number

    get_admission_number.short_description = 'Admission Number'
    get_admission_number.admin_order_field = 'qr_code__candidate__admission_number'

    actions = ['generate_scan_report']

    def generate_scan_report(self, request, queryset):
        total_scans = queryset.count()
        unique_candidates = queryset.values('qr_code__candidate').distinct().count()
        most_scanned_location = queryset.values('location').annotate(count=Count('location')).order_by('-count').first()

        message = f"Total Scans: {total_scans}<br>"
        message += f"Unique Candidates Scanned: {unique_candidates}<br>"
        if most_scanned_location:
            message += f"Most Scanned Location: {most_scanned_location['location']} ({most_scanned_location['count']} scans)<br>"

        self.message_user(request, mark_safe(message))

    generate_scan_report.short_description = "Generate Scan Report"
