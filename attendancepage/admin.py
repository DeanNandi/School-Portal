from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from .models import ClassAttendance


@admin.register(ClassAttendance)
class ClassAttendanceAdmin(ImportExportModelAdmin):
    list_display = ('candidate_full_name', 'date', 'present_status', 'absent_reason', 'user')
    list_filter = ('candidate__First_Name', 'candidate__Last_Name', 'user', 'present', 'absent_reason', 'date',)
    search_fields = ('candidate__First_Name', 'candidate__Last_Name', 'user__username', 'absent_reason')
    date_hierarchy = 'date'
    list_per_page = 15
    actions = ['mark_as_present', 'mark_as_absent']

    fieldsets = (
        ('Attendance Information', {
            'fields': ('candidate', 'date', 'present', 'absent_reason')
        }),
        ('User Information', {
            'fields': ('user',),
            'classes': ('collapse',),
        }),
    )

    def candidate_full_name(self, obj):
        return f"{obj.candidate.First_Name} {obj.candidate.Last_Name}"

    candidate_full_name.short_description = "Student Name"

    def present_status(self, obj):
        if obj.present:
            return format_html('<span style="color: green;">Present</span>')
        return format_html('<span style="color: red;">Absent</span>')

    present_status.short_description = "Attendance Status"

    def mark_as_present(self, request, queryset):
        updated = queryset.update(present=True, absent_reason=None)
        self.message_user(request, f"{updated} attendances marked as present.")

    mark_as_present.short_description = "Mark selected attendances as present"

    def mark_as_absent(self, request, queryset):
        updated = queryset.update(present=False)
        self.message_user(request, f"{updated} attendances marked as absent.")

    mark_as_absent.short_description = "Mark selected attendances as absent"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _attendance_count=Count('candidate')
        )
        return queryset

    def attendance_count(self, obj):
        return obj._attendance_count

    attendance_count.admin_order_field = '_attendance_count'
    attendance_count.short_description = 'Total Attendances'

    def view_candidate(self, obj):
        url = reverse('admin:studentpage_candidate_change', args=[obj.candidate.id])
        return mark_safe(f'<a href="{url}">View Candidate</a>')

    view_candidate.short_description = 'Student Details'

    readonly_fields = ('view_candidate', 'attendance_count')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('candidate', 'date')
        return self.readonly_fields

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)
