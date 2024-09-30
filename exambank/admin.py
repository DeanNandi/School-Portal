from django.contrib import admin
from .models import ExamMenschen, ExamFile


class ExamMenschenInline(admin.TabularInline):
    model = ExamMenschen
    extra = 1  # Number of empty forms to display


@admin.register(ExamMenschen)
class ExamMenschenAdmin(admin.ModelAdmin):
    list_display = ('get_exam_name', 'exam_file', 'date_uploaded')
    list_filter = ('exam__exam_name', 'date_uploaded')
    list_per_page = 10

    def get_exam_name(self, obj):
        return f"{obj.exam.class_level} {obj.exam.exam_name}"

    get_exam_name.short_description = 'Exam Name'


@admin.register(ExamFile)
class ExamFileAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'exam_name')
    list_filter = ('class_level',)
    list_per_page = 10

    # Add the inline for Transcripts
    inlines = [ExamMenschenInline]
