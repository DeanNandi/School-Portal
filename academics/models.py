from django.db import models
from studentpage.models import Candidate
from teacherpage.models import Cohort
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
# Examination reports
from teacherpage.models import Teacher

missed_assessment_reasons = [
    ('Sick', 'Sick'),
    ('Personal Reason', 'Personal Reason'),
    ('Missed without Excuse', 'Missed without Excuse'),
]


class Examination(models.Model):
    examination_name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    class_information = models.ForeignKey(Cohort, on_delete=models.CASCADE, null=True, blank=True)
    class_level_select = (
        ('A1.1', 'A1.1'),
        ('A1.2', 'A1.2'),
        ('A2.1', 'A2.1'),
        ('A2.2', 'A2.2'),
        ('B1.1', 'B1.1'),
        ('B1.2', 'B1.2'),
        ('B2.1', 'B2.1'),
        ('B2.2', 'B2.2'),
        ('Custom name', 'Custom name'),
    )
    class_level = models.CharField(max_length=50, choices=class_level_select, null=True, blank=True)
    date_added = models.DateField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='examinations')

    def __str__(self):
        return f"{self.examination_name} - {self.class_information}"


class StudentExam(models.Model):
    name_of_exam = models.ForeignKey(Examination, on_delete=models.CASCADE)
    student = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    percentage_score = models.CharField(max_length=255, null=True, blank=True)  # Keeping this as CharField
    missed_exam_reason = models.CharField(max_length=255, choices=missed_assessment_reasons, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_exams')

    speaking_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    listening_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reading_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    writing_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    speaking_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    listening_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reading_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    writing_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    speaking_missed_reason = models.CharField(max_length=255, choices=missed_assessment_reasons, null=True, blank=True)
    listening_missed_reason = models.CharField(max_length=255, choices=missed_assessment_reasons, null=True, blank=True)
    reading_missed_reason = models.CharField(max_length=255, choices=missed_assessment_reasons, null=True, blank=True)
    writing_missed_reason = models.CharField(max_length=255, choices=missed_assessment_reasons, null=True, blank=True)

    def __str__(self):
        return f"{self.name_of_exam}"

    def calculate_percentage_score(self):
        skills = ['speaking', 'listening', 'reading', 'writing']
        skill_percentages = []
        for skill in skills:
            score = getattr(self, f'{skill}_score')
            total = getattr(self, f'{skill}_total')
            if score is not None and total is not None and Decimal(total) > 0:
                percentage = (Decimal(score) / Decimal(total)) * 100
                skill_percentages.append(percentage)
        if skill_percentages:
            average = sum(skill_percentages) / len(skill_percentages)
            return f"{average:.2f}%"  # Returning as a string with % symbol
        return None

    def calculate_and_save_percentage_score(self):
        self.percentage_score = self.calculate_percentage_score()
        self.save()

    def save(self, *args, **kwargs):
        if not self.percentage_score:
            self.percentage_score = self.calculate_percentage_score()
        super().save(*args, **kwargs)

    @property
    def percentage_score_as_decimal(self):
        if self.percentage_score:
            try:
                return Decimal(self.percentage_score.rstrip('%'))
            except ValueError:
                return None
        return None


class ExaminationReport(models.Model):
    WAY_FORWARD_CHOICES = [
        ('Defer student', 'Defer student'),
        ('Student stays in class', 'Student stays in class'),
        ('Repeat class', 'Repeat class'),
    ]
    ADMIN_DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]

    student_exam = models.OneToOneField(StudentExam, on_delete=models.CASCADE, related_name='examination_report')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    speaking_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    listening_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reading_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    writing_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teachers_notes = models.TextField(blank=True)
    way_forward = models.CharField(max_length=50, choices=WAY_FORWARD_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New fields for admin approval
    admin_decision = models.CharField(max_length=10, choices=ADMIN_DECISION_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    admin_decision_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report for {self.candidate.First_Name} {self.candidate.Last_Name} - {self.student_exam.name_of_exam}"

    def save(self, *args, **kwargs):
        if self.admin_decision in ['approved', 'rejected'] and not self.admin_decision_date:
            self.admin_decision_date = timezone.now()
        super().save(*args, **kwargs)


class ClassReport(models.Model):
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE)
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE)
    overall_report = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('examination', 'cohort')

    def __str__(self):
        return f"Class Report for {self.cohort.course_class_no} - {self.examination.examination_name}"


class ScheduledExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_exam_dates')
    examination = models.ForeignKey('Examination', on_delete=models.CASCADE, related_name='scheduled_dates')
    scheduled_date = models.DateTimeField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'examination')

    def __str__(self):
        return f"{self.examination} scheduled by {self.user} for {self.scheduled_date}"