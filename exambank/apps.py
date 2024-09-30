from django.apps import AppConfig


class ExamBankConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exambank'
    verbose_name = 'Exam Bank'  # This is the human-readable name for the admin.
