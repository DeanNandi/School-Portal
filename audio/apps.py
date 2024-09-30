from django.apps import AppConfig


class AudioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audio'
    verbose_name = 'Audio Files and Documents'  # This is the human-readable name for the admin.
