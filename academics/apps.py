from django.apps import AppConfig


class AcademicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academics'
    verbose_name = 'Academic Information and Records'  # This is the human-readable name for the admin.

