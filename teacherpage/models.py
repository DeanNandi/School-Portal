from django.db import models
from attendancepage.models import ClassAttendance
from django.contrib.auth.models import User
from studentpage.models import Candidate


class Update(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Teacher(models.Model):
    needs_password_change = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher', blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    passport_photo = models.ImageField(upload_to='teacher_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('other', 'Other')
    )
    sex = models.CharField(max_length=50, null=True, choices=SEX, default='None')
    email_address = models.EmailField(max_length=70, blank=True, null=True, unique=True)
    nationality_choice = (
        ('Kenyan', 'Kenyan'),
        ('Other', 'Other')
    )
    nationality = models.CharField(max_length=45, choices=nationality_choice, blank=True, null=True, )
    religion_choice = (
        ('Islam', 'Islam'),
        ('Hinduism', 'Hinduism'),
        ('Buddhism', 'Buddhism'),
        ('Christian', 'Christian'),
        ('Other', 'Other')
    )
    religion = models.CharField(max_length=45, choices=religion_choice, blank=True, null=True, )
    COURSE_LOCATION = (
        ('Nairobi_CBD', 'Nairobi_CBD'),
        ('Nairobi_Hospital', 'Nairobi_Hospital'),
        ('Nairobi_Karen', 'Nairobi_Karen'),
        ('Nairobi_Daystar', 'Nairobi_Daystar'),
        ('Mombasa', 'Mombasa'),
        ('Muranga', 'Muranga'),
        ('Kisumu', 'Kisumu'),
        ('Kisii', 'Kisii'),
        ('Eldoret', 'Eldoret'),
        ('Thika', 'Thika'),

    )
    course_location = models.CharField(max_length=255, choices=COURSE_LOCATION, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CourseIntake(models.Model):
    course_intake = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course_intake}"


class Cohort(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    course_class_no = models.CharField(max_length=255)
    course_intake = models.ForeignKey(CourseIntake, on_delete=models.CASCADE, null=True,
                                      blank=True)  # Correct reference to the model
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course_intake} - {self.course_class_no} ({self.teacher})"
