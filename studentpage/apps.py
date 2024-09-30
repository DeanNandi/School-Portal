from django.apps import AppConfig


class StudentpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studentpage'
    verbose_name = 'Student Records'  # This is the human-readable name for the admin.
