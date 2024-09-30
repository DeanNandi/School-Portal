from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'files'
    verbose_name = 'Books and Documents'  # This is the human-readable name for the admin.

