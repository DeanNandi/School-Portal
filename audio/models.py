from django.db import models


class AudioFile(models.Model):
    CLASS_ASSIGNMENT = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
    )
    class_level = models.CharField(max_length=50, choices=CLASS_ASSIGNMENT, default='Not-Set')
    audio_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.class_level} - {self.audio_name}"


class AudioMenschen(models.Model):
    audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE, blank=True, null=True)
    zip_file = models.FileField(upload_to='audio_zip/', blank=True, null=True)
    date_uploaded = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.audio} - {self.date_uploaded}"


class AudioGrammatik_Aktiv(models.Model):
    audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE, blank=True, null=True)
    zip_file = models.FileField(upload_to='audio_zip/', blank=True, null=True)
    date_uploaded = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.audio} - {self.date_uploaded}"
