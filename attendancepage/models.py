from django.db import models
from studentpage.models import Candidate
from django.conf import settings


ABSENT_REASON_CHOICES = [
    ('Too Late', 'Too Late'),
    ('Absent with Excuse', 'Absent with Excuse'),
    ('Absent without Excuse', 'Absent without Excuse'),
]


class ClassAttendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_attendance',
                             null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    date = models.DateField()
    present = models.BooleanField()
    absent_reason = models.CharField(max_length=255, choices=ABSENT_REASON_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} - {self.date}"
