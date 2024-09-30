from django.db import models


class ExamFile(models.Model):
    CLASS_ASSIGNMENT = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),

    )
    class_level = models.CharField(max_length=50, choices=CLASS_ASSIGNMENT, default='Not-Set')
    exam_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.class_level} - {self.exam_name}"


class ExamMenschen(models.Model):
    exam = models.ForeignKey(ExamFile, on_delete=models.CASCADE, blank=True, null=True)
    exam_file = models.FileField(upload_to='exam/')
    date_uploaded = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.exam} - {self.exam_file}"
