from django.contrib import admin
from django.core.management import call_command
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from django.db.models.fields.files import FileField, ImageField
from django.contrib import messages
from .models import UploadedDocument
from .models import Candidate, Transcript, PasswordResetCode
from django.utils.html import format_html
from django.utils import timezone
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'version', 'is_current', 'created_at', 'updated_at')
    list_filter = ('is_current', 'candidate')
    search_fields = ('candidate__First_Name', 'candidate__Last_Name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Candidate Information', {
            'fields': ('candidate', 'version', 'is_current')
        }),
        ('Personal Statement', {
            'fields': ('summary',)
        }),
        ('Experience and Education', {
            'fields': ('work_experiences', 'educations')
        }),
        ('Skills', {
            'fields': ('technical_skills', 'soft_skills')
        }),
        ('Additional Qualifications', {
            'fields': ('languages', 'certifications', 'projects', 'volunteer_experiences')
        }),
        ('Achievements and Publications', {
            'fields': ('awards', 'publications')
        }),
        ('Professional Information', {
            'fields': ('memberships', 'references')
        }),
        ('Personal Interests', {
            'fields': ('interests',)
        }),
        ('Additional Information', {
            'fields': ('additional_info',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_current:
            # Set all other resumes of this candidate to not current
            Resume.objects.filter(candidate=obj.candidate).update(is_current=False)
        super().save_model(request, obj, form, change)


class TranscriptInline(admin.TabularInline):
    model = Transcript
    extra = 1  # Number of empty forms to display


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'file_link')
    list_filter = ('candidate',)

    def file_link(self, obj):
        if obj.other_transcripts:  # Changed from 'file' to 'other_transcripts'
            return format_html(f'<a href="{obj.other_transcripts.url}" target="_blank">View File</a>')
        return "No file uploaded"

    file_link.short_description = 'Transcript File'


def import_candidates(modeladmin, request, queryset):
    # Assuming the path to your JSON file is static; adjust as needed
    json_file_path = 'C:\\Users\\Dell\\PycharmProjects\\Agcrm\\candidates_export.json'

    try:
        # Call your custom command directly
        call_command('import_updated_candidates', json_file_path)
        modeladmin.message_user(request, "Candidates imported successfully.")
    except Exception as e:
        modeladmin.message_user(request, f"Error importing candidates: {e}")


import_candidates.short_description = "Import Candidates from AGCRM"


def make_delete_action(field):
    """Factory function to create a custom action for deleting a specific file field."""

    def delete_file(modeladmin, request, queryset):
        for obj in queryset:
            file_field = getattr(obj, field.name, None)
            if file_field:
                file_field.delete(save=True)
                setattr(obj, field.name, None)
                obj.save()
                messages.success(request, f'Successfully deleted {field.name.replace("_", " ")} for {obj}.')
            else:
                messages.warning(request, f'No file found in {field.name.replace("_", " ")} for {obj}.')

    delete_file.short_description = f"Delete {field.name.replace('_', ' ')}"
    delete_file.__name__ = f'delete_{field.name}'

    return delete_file


class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ['First_Name', 'Last_Name', 'admission_number', 'Course_Location', 'display_files']
    list_filter = ['First_Name', 'Last_Name', 'admission_number', 'Course_Location']
    list_per_page = 30

    def get_actions(self, request):
        actions = super().get_actions(request)
        file_fields = [f for f in self.model._meta.get_fields() if isinstance(f, (FileField, ImageField))]
        for field in file_fields:
            action = make_delete_action(field)
            self.admin_site.add_action(action)
            actions[action.__name__] = (action, action.__name__, action.short_description)
        return actions

    def display_files(self, obj):
        links = [format_html('<a href="{}">{}</a>', getattr(obj, f.name).url, f.name.replace('_', ' ').title())
                 for f in obj._meta.fields if isinstance(f, FileField) and getattr(obj, f.name)]
        return format_html('<br>'.join(links))

    display_files.short_description = "Files"


admin.site.register(UploadedDocument, UploadedDocumentAdmin)


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'masked_code', 'created_at', 'is_expired', 'attempts', 'user_email')
    list_filter = ('user', 'created_at', 'attempts')
    search_fields = ('user__username', 'user__email', 'code')
    list_per_page = 10
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'code', 'attempts', 'masked_code', 'is_expired')

    fields = ('user', 'code', 'masked_code', 'created_at', 'is_expired', 'attempts')

    def masked_code(self, obj):
        return f"{'*' * 4}{obj.code[-2:]}"

    masked_code.short_description = 'Masked Code'

    def is_expired(self, obj):
        expiration_time = obj.created_at + timezone.timedelta(minutes=15)
        is_expired = timezone.now() > expiration_time
        return format_html(
            '<span style="color: {};">{}</span>',
            'red' if is_expired else 'green',
            'Expired' if is_expired else 'Active'
        )

    is_expired.short_description = 'Expiration Status'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'User Email'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        return queryset

    def has_add_permission(self, request):
        return False  # Prevent manual creation of reset codes


@admin.register(Candidate)
class CandidateAdmin(ImportExportModelAdmin):
    list_display = ('First_Name', 'Last_Name', 'admission_number', 'email_address', 'Course_Location', 'course_intake')
    list_filter = ('First_Name', 'Last_Name', 'admission_number', 'email_address', 'Course_Location', 'course_intake')
    search_fields = ('First_Name', 'Last_Name', 'email_address', 'phone_number', 'admission_number')
    readonly_fields = ('admission_number',)
    list_per_page = 15

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'First_Name', 'Last_Name', 'Date_of_Birth', 'Sex', 'photo', 'Address', 'Street_Address',
                'Other_Address', 'Zip_Address'
            )
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'secondary_phone_number', 'email_address', 'secondary_email_address')
        }),
        ('Education', {
            'fields': (
                'Qualification', 'High_School_name', 'High_School_Year', 'High_School_grade', 'University_Name',
                'Degree', 'GPA'
            )
        }),
        ('Language Skills', {
            'fields': ('fluency_in_language', 'Level_Of_German', 'german_file', 'english_file')
        }),
        ('Course Information', {
            'fields': ('course_intake', 'Course_Location', 'admission_number', 'Time')
        }),
        ('Documents', {
            'fields': (
                'Birth_certificate', 'certificate_of_good_conduct', 'passport', 'Licence_file', 'Nursing_Certificate',
                'resume_file', 'identification_card_file'
            )
        }),
        ('Credentials', {
            'fields': ('needs_password_change', 'username', 'user')
        }),
    )

    def full_name(self, obj):
        return f"{obj.First_Name} {obj.Last_Name}"

    full_name.short_description = 'Full Name'

    # Add the inline for Transcripts
    inlines = [TranscriptInline]


admin.site.index_title = "Welcome to AG German Institute Admin Portal"

