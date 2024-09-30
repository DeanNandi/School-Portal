from django.contrib import admin
from django.contrib.auth.models import User
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Examination, StudentExam
from studentpage.models import Candidate
from django.utils.html import format_html
from django.db.models import Avg, Value
from django.db.models.functions import Cast, Replace
from django.db.models import FloatField
# ExamReports
from .models import ExaminationReport, ClassReport, ScheduledExam


@admin.register(ScheduledExam)
class ScheduledExamAdmin(admin.ModelAdmin):
    list_display = ('user', 'examination', 'scheduled_date', 'date_added', 'date_updated')
    list_filter = ('examination', 'scheduled_date')
    search_fields = ('user__username', 'examination__name')  # Assuming 'name' is a field in the Examination model
    date_hierarchy = 'scheduled_date'

    fieldsets = (
        ('User and Examination', {
            'fields': ('user', 'examination')
        }),
        ('Schedule Information', {
            'fields': ('scheduled_date',)
        }),
        ('Metadata', {
            'fields': ('date_added', 'date_updated'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('date_added', 'date_updated')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'examination')

admin.site.register(StudentExam)
@admin.register(ClassReport)
class ClassReportAdmin(admin.ModelAdmin):
    list_display = ('get_examination_display', 'get_cohort_details', 'created_at', 'updated_at')
    list_filter = ('examination__class_level', 'cohort__teacher', 'cohort__course_intake')
    search_fields = ('examination__examination_name', 'examination__class_level',
                     'cohort__course_class_no', 'cohort__teacher__first_name',
                     'cohort__teacher__last_name', 'cohort__course_intake__course_intake')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Report Information', {
            'fields': ('examination', 'cohort')
        }),
        ('Report Content', {
            'fields': ('overall_report',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_examination_display(self, obj):
        if obj.examination.examination_name:
            return obj.examination.examination_name
        return obj.examination.class_level

    get_examination_display.short_description = 'Examination'
    get_examination_display.admin_order_field = 'examination__examination_name'

    def get_cohort_details(self, obj):
        teacher_name = f"{obj.cohort.teacher.first_name} {obj.cohort.teacher.last_name}" if obj.cohort.teacher else "No teacher assigned"
        course_intake = obj.cohort.course_intake.course_intake if obj.cohort.course_intake else "No intake assigned"
        return f"{obj.cohort.course_class_no} - {teacher_name} - {course_intake}"

    get_cohort_details.short_description = 'Cohort Details'
    get_cohort_details.admin_order_field = 'cohort__course_class_no'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('examination', 'cohort')
        return self.readonly_fields


class ExaminationReportResource(resources.ModelResource):
    class Meta:
        model = ExaminationReport
        fields = ('id', 'student_exam', 'candidate', 'teacher', 'speaking_score', 'listening_score',
                  'reading_score', 'writing_score', 'teachers_notes', 'way_forward', 'created_at', 'updated_at')


@admin.register(ExaminationReport)
class ExaminationReportAdmin(ImportExportModelAdmin):
    resource_class = ExaminationReportResource
    list_display = ('candidate', 'teacher', 'teachers_notes', 'way_forward', 'created_at', 'updated_at')
    list_filter = ('way_forward', 'teacher', 'created_at', 'updated_at')
    search_fields = (
        'candidate__First_Name', 'candidate__Last_Name', 'teacher__first_name', 'teacher__last_name', 'teachers_notes')
    date_hierarchy = 'created_at'
    list_per_page = 25

    fieldsets = (
        ('Examination Information', {
            'fields': ('student_exam', 'candidate', 'teacher'),
            'description': 'Basic information about the examination report.'
        }),
        ('Scores', {
            'fields': ('speaking_score', 'listening_score', 'reading_score', 'writing_score'),
            'description': 'Individual scores for each skill.',
            'classes': ('collapse',),
        }),
        ('Teacher\'s Evaluation', {
            'fields': ('teachers_notes', 'way_forward'),
            'description': 'Teacher\'s notes and decision on the way forward for the student.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'When the report was created and last updated.',
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def display_scores(self, obj):
        scores = [
            f"Speaking: {obj.speaking_score}",
            f"Listening: {obj.listening_score}",
            f"Reading: {obj.reading_score}",
            f"Writing: {obj.writing_score}"
        ]
        return format_html("<br>".join(scores))

    display_scores.short_description = 'Scores'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('student_exam', 'candidate', 'teacher')
        return queryset

    def get_summary_metrics(self, request):
        queryset = self.get_queryset(request)
        avg_scores = queryset.aggregate(
            avg_speaking=Avg('speaking_score'),
            avg_listening=Avg('listening_score'),
            avg_reading=Avg('reading_score'),
            avg_writing=Avg('writing_score')
        )
        return {
            'total_reports': queryset.count(),
            'avg_scores': {k: f"{v:.2f}" if v else "N/A" for k, v in avg_scores.items()},
            'way_forward_counts': {k: queryset.filter(way_forward=k).count() for k, _ in
                                   ExaminationReport.WAY_FORWARD_CHOICES},
        }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['summary_metrics'] = self.get_summary_metrics(request)
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        css = {
            'all': ('admin/css/examination_reports_admin.css',)
        }





admin.site.register(Examination)