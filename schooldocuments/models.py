from django.db import models
from studentpage.models import Candidate


class Admission(models.Model):
    Name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    Date_of_Admission = models.DateField()
    GERMAN_LEVEL = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
    )
    German_Level = models.CharField(max_length=50, null=True, choices=GERMAN_LEVEL, default='None')
    pdf_file = models.FileField(upload_to='admissions/', null=True, blank=True)


class Contract(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='contract')
    signed_contract = models.FileField(upload_to='students_contracts/', null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} {self.signed_contract}"
