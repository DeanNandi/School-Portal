from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Teacher, Cohort, CourseIntake, Update


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'description_preview', 'icon', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'icon')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'icon')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description

    description_preview.short_description = 'Description'

    def icon_display(self, obj):
        return f'<i class="bi {obj.icon}"></i>'

    icon_display.short_description = 'Icon'
    icon_display.allow_tags = True

    list_display_links = ('title', 'description_preview')
    list_per_page = 20
    date_hierarchy = 'created_at'
    save_on_top = True


admin.site.register(Update, UpdateAdmin)


class CohortInline(admin.TabularInline):
    model = Cohort
    extra = 1  # Number of empty forms to display


@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_name', 'course_intake', 'course_class_no')
    list_filter = ('teacher__first_name', 'course_intake', 'course_class_no')
    list_per_page = 10

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    get_teacher_name.short_description = 'Teacher Name'


admin.site.register(CourseIntake)


@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    list_display = ('first_name', 'last_name', 'sex', 'email_address', 'phone_number')
    list_filter = ('first_name', 'last_name', 'phone_number')
    list_per_page = 10

    # Add the inline for Transcripts
    inlines = [CohortInline]
