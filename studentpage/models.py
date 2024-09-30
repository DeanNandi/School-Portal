from multiselectfield import MultiSelectField
# Password Reset
from django.contrib.auth import get_user_model
import random
import string
from django.utils import timezone
from datetime import timedelta
from django.db import models

User = get_user_model()


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))

    @classmethod
    def can_send_email(cls, user):
        # Check if the user has exceeded the limit in the past 24 hours
        yesterday = timezone.now() - timedelta(hours=24)
        attempts = cls.objects.filter(user=user, created_at__gte=yesterday).count()
        return attempts < 3  # Limit to 3 attempts per 24 hours


class Candidate(models.Model):
    candidate_type = models.CharField(max_length=255, null=True, blank=True)
    target_level = models.CharField(max_length=255, null=True, blank=True)
    partnership = models.CharField(max_length=255, null=True, blank=True)
    class_schedule = models.CharField(max_length=255, null=True, blank=True)

    # Notes
    notes = models.JSONField(default=list, blank=True, null=True)
    device_mac_address = models.CharField(max_length=17, unique=True, null=True, blank=True)
    sponsored = models.BooleanField(default=False)
    # new field for passwords
    needs_password_change = models.BooleanField(default=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate', blank=True, null=True)
    First_Name = models.CharField(max_length=255)
    Last_Name = models.CharField(max_length=255)
    Date_of_Birth = models.DateField(max_length=50, blank=True, null=True)
    # birth certificate
    Birth_certificate = models.FileField(upload_to='Birth_certificates/', null=True, blank=True)
    SEX = (
        ('None', 'None'),
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    Sex = models.CharField(max_length=50, null=True, choices=SEX, default='None')
    ADDRESS = (
        ('Mombasa', 'Mombasa (001)'),
        ('Kwale', 'Kwale (002 )'),
        ('Kilifi', 'Kilifi (003)'),
        ('Tana River', 'Tana River (004)'),
        ('Lamu', 'Lamu (005)'),
        ('Taita–Taveta', 'Taita–Taveta (006)'),
        ('Garissa', 'Garissa (007)'),
        ('Wajir', 'Wajir (008)'),
        ('Mandera', 'Mandera (009)'),
        ('Marsabit', 'Marsabit (010)'),
        ('Isiolo', 'Isiolo (011)'),
        ('Meru', 'Meru (012)'),
        ('Tharaka-Nithi', 'Tharaka-Nithi (013)'),
        ('Embu', 'Embu (014)'),
        ('Kitui', 'Kitui (015)'),
        ('Makueni', 'Makueni (017)'),
        ('Nyandarua', 'Nyandarua (018)'),
        ('Nyeri', 'Nyeri (019)'),
        ('Kirinyaga', 'Kirinyaga (020)'),
        ('Muranga', 'Muranga (021)'),
        ('Kiambu', 'Kiambu (022)'),
        ('Turkana', 'Turkana (023)'),
        ('West Pokot', 'West Pokot (024)'),
        ('Samburu', 'Samburu (025)'),
        ('Trans-Nzoia', 'Trans-Nzoia (026)'),
        ('Uasin Gishu', 'Uasin Gishu (027)'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet (028)'),
        ('Nandi Kapsabet', 'Nandi Kapsabet (029)'),
        ('Baringo Kabarnet', 'Baringo Kabarnet (030)'),
        ('Laikipia', 'Laikipia (031)'),
        ('Nakuru', 'Nakuru (032)'),
        ('Narok', 'Narok (033)'),
        ('Kajiado', 'Kajiado (034)'),
        ('Kericho', 'Kericho (035)'),
        ('Bomet', 'Bomet (036)'),
        ('Kakamega', 'Kakamega (037)'),
        ('Vihiga', 'Vihiga (038)'),
        ('Bungoma', 'Bungoma (039)'),
        ('Busia', 'Busia (040)'),
        ('Siaya', 'Siaya (041)'),
        ('Kisumu', 'Kisumu (042)'),
        ('Homa Bay', 'Homa Bay (043)'),
        ('Migori', 'Migori (044)'),
        ('Kisii', 'Kisii (045)'),
        ('Nyamira', 'Nyamira (046)'),
        ('Nairobi', 'Nairobi (047)'),

    )
    Address = models.CharField(max_length=100, null=True, choices=ADDRESS, default='Other')
    # cohorts updated
    course_intake = models.CharField(max_length=255, blank=True, null=True)
    # image candidate
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    # cert of good conduct
    certificate_of_good_conduct = models.FileField(upload_to='certificates_of_good_conduct/', null=True, blank=True)
    # Passports
    passport = models.FileField(upload_to='candidate_passports/', null=True, blank=True)
    Street_Address = models.CharField(max_length=512, blank=True, null=True)
    Other_Address = models.CharField(max_length=50, blank=True, null=True)
    Zip_Address = models.CharField(max_length=50, blank=True, null=True)
    LANGUAGE = (
        ('None', 'None'),
        ('English Beginner', 'English Beginner'),
        ('English Intermediate', 'English Intermediate'),
        ('English Advanced', 'English Advanced'),
    )
    fluency_in_language = models.CharField(max_length=50, null=True, choices=LANGUAGE, default='None')
    english_file = models.FileField(blank=True, null=True)
    GERMAN = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
    )
    Level_Of_German = models.CharField(max_length=50, null=True, choices=GERMAN, default='None')
    german_file = models.FileField(blank=True, null=True)
    YES_or_NO = (
        ('Pending', 'Pending'),
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    Spouse = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    Spouse_Name = models.CharField(max_length=512, blank=True, null=True)
    Children = models.CharField(max_length=50, null=True, choices=YES_or_NO, default='Pending')
    Child_name = models.CharField(max_length=512, blank=True, null=True)
    child_sex = models.CharField(max_length=255, choices=SEX, default='None')
    child_date_of_birth = models.CharField(max_length=512, blank=True, null=True)
    Child_name2 = models.CharField(max_length=512, blank=True, null=True)
    child_sex2 = models.CharField(max_length=255, choices=SEX, default='None')
    child_date_of_birth2 = models.CharField(max_length=512, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    secondary_phone_number = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=512, blank=True, null=True)
    emergency_phone_number = models.CharField(max_length=50, blank=True, null=True)
    email_address = models.EmailField(max_length=70, blank=True, null=True)
    secondary_email_address = models.EmailField(max_length=70, blank=True, null=True)
    Licence_No = models.CharField(max_length=100, blank=True, null=True)
    Licence_file = models.FileField(blank=True, null=True)
    # nursing certificate
    Nursing_Certificate = models.FileField(blank=True, null=True)
    QUALIFICATION = (
        ('Kenya Registerd Community Health Nurse (KRCHN)', 'Kenya Registerd Community Health Nurse (KRCHN)'),
        ('Kenya Enrolled Community Health Nurse (KECHN)', 'Kenya Enrolled Community Health Nurse (KECHN)'),
        ('B.Sc Nursing (BSN)', 'B.Sc Nursing (BSN)'),
        ('Newly Graduated Nursing Student (diploma/BSN)', 'Newly Graduated Nursing Student (diploma/BSN)'),
        ('Nurse Aid', 'Nurse Aid'),
        ('Clinical Officer', 'Clinical Officer'),
        ('Kenya Registered Nursing (KRN)', 'Kenya Registered Nursing (KRN)'),
        ('ECE Teachers (Early Childhood Education Teacher)', 'ECE Teachers (Early Childhood Education Teacher)'),
        ('Other Qualification', 'Other Qualification'),
    )
    # qualification
    Qualification = models.CharField(max_length=255, choices=QUALIFICATION, null=True)
    # end of it
    High_School_name = models.CharField(max_length=512, blank=True, null=True)
    High_School_Year_start = models.CharField(max_length=4, blank=True, null=True)
    High_School_grade = models.CharField(max_length=3, blank=True, null=True)
    High_School_Year = models.CharField(max_length=4, blank=True, null=True)
    High_School_file = models.FileField(blank=True, null=True)
    # Uni one
    University_Name = models.CharField(max_length=512, blank=True, null=True)
    Degree = models.CharField(max_length=512, blank=True, null=True)
    GPA = models.CharField(max_length=10, blank=True, null=True)
    University_Year_start = models.CharField(max_length=4, blank=True, null=True)
    University_Year = models.CharField(max_length=4, blank=True, null=True)
    University_file = models.FileField(blank=True, null=True)
    # uni two
    University_Name_secondary = models.CharField(max_length=512, blank=True, null=True)
    Degree_secondary = models.CharField(max_length=100, blank=True, null=True)
    GPA_secondary = models.CharField(max_length=10, blank=True, null=True)
    University_secondary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    University_Year_secondary = models.CharField(max_length=4, blank=True, null=True)
    University_secondary_file = models.FileField(blank=True, null=True)
    # uni three
    University_Name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    University_tertiary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Degree_tertiary = models.CharField(max_length=100, blank=True, null=True)
    GPA_tertiary = models.CharField(max_length=10, blank=True, null=True)
    University_Year_tertiary = models.CharField(max_length=4, blank=True, null=True)
    University_tertiary_file = models.FileField(blank=True, null=True)
    # college one
    College_Name = models.CharField(max_length=512, blank=True, null=True)
    College_Degree_Year_start = models.CharField(max_length=4, blank=True, null=True)
    College_Degree = models.CharField(max_length=100, blank=True, null=True)
    College_GPA = models.CharField(max_length=10, blank=True, null=True)
    College_Year = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_file = models.FileField(blank=True, null=True)
    # college two
    College_Name_secondary = models.CharField(max_length=512, blank=True, null=True)
    College_Degree_secondary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_secondary = models.CharField(max_length=100, blank=True, null=True)
    College_GPA_secondary = models.CharField(max_length=10, blank=True, null=True)
    College_Year_Secondary = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_secondary_file = models.FileField(blank=True, null=True)
    # college three
    College_Name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    College_tertiary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    College_Degree_tertiary = models.CharField(max_length=100, blank=True, null=True)
    College_GPA_tertiary = models.CharField(max_length=10, blank=True, null=True)
    College_Year_tertiary = models.CharField(max_length=4, blank=True, null=True)
    College_tertiary_file = models.FileField(blank=True, null=True)
    # Institution one
    Institution_name = models.CharField(max_length=512, blank=True, null=True)
    Ward_name = models.CharField(max_length=512, blank=True, null=True)
    Hours_worked = models.CharField(max_length=512, blank=True, null=True)
    Institution_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Institution_Year_end = models.CharField(max_length=4, blank=True, null=True)
    Institution_file = models.FileField(blank=True, null=True)
    # Institution two
    Institution_name_secondary = models.CharField(max_length=512, blank=True, null=True)
    Ward_name_secondary = models.CharField(max_length=512, blank=True, null=True)
    Hours_worked_secondary = models.CharField(max_length=512, blank=True, null=True)
    Institution_secondary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Institution_secondary_Year_end = models.CharField(max_length=4, blank=True, null=True)
    Institution_file_secondary = models.FileField(blank=True, null=True)
    # Institution three
    Institution_name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    Ward_name_tertiary = models.CharField(max_length=512, blank=True, null=True)
    Hours_worked_tertiary = models.CharField(max_length=512, blank=True, null=True)
    Institution_tertiary_Year_end = models.CharField(max_length=4, blank=True, null=True)
    Institution_tertiary_Year_start = models.CharField(max_length=4, blank=True, null=True)
    Institution_file_tertiary = models.FileField(blank=True, null=True)
    COURSE_LOCATION = (
        ('Online', 'Online'),
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
    # updated location
    Course_Location = models.CharField(max_length=50, choices=COURSE_LOCATION, null=True, )
    # end
    DAYS = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),

    )
    Days = MultiSelectField(max_length=50, choices=DAYS, blank=True, null=True)
    TIME = (
        ('None', 'None'),
        ('morning (around 9:30 - 13:00)', 'morning (around 9:30 - 13:00)'),
        ('afternoon (around 13:30 - 17:00)', 'afternoon (around 13:30 - 17:00)'),
        ('evening (around 17:30 - 20:30)', 'evening (around 17:30 - 20:30)'),
        ('online (evening)', 'online (evening)'),
    )
    Time = models.CharField(max_length=50, null=True, choices=TIME, default='None')
    RESULTS = (
        ('Paid', 'Paid'),
        ('Not-Paid', 'Not-Paid')
    )
    Results = models.CharField(max_length=50, blank=True, null=True, choices=RESULTS, default='Not-Paid')
    Schedule_Interview_date = models.DateField(max_length=50, blank=True, null=True)
    Schedule_Interview_time = models.TimeField(max_length=50, blank=True, null=True)
    admission_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    # New fields
    resume_file = models.FileField(upload_to='resume_files/', blank=True, null=True)
    identification_card_file = models.FileField(upload_to='identification_cards/', blank=True, null=True)

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name}"

    @property
    def full_name(self):
        return f"{self.First_Name} {self.Last_Name}"


class UploadedDocument(Candidate):
    class Meta:
        proxy = True  # This model will not create a new table in the database but extend the 'Candidate' model

    def file_fields(self):
        """
        Generates a list of tuples for each file field in the model,
        containing the field's name and the URL of the associated file.
        """
        files_info = []
        for field in self._meta.fields:
            if isinstance(field, models.FileField) and getattr(self, field.name):
                file_instance = getattr(self, field.name)
                files_info.append((field.name, file_instance.url))
        return files_info


class Transcript(models.Model):
    candidate = models.ForeignKey(Candidate, related_name='transcripts', on_delete=models.CASCADE)
    other_transcripts = models.FileField(upload_to='candidate_transcripts/')


# MAXWELL
from django.db import models
from django.utils import timezone


class Resume(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='resumes')

    # Version control
    version = models.PositiveIntegerField(default=1)
    is_current = models.BooleanField(default=True)

    # Personal Statement
    summary = models.TextField(blank=True, null=True, help_text="A brief personal statement or career objective")

    # Work Experience
    work_experiences = models.TextField(blank=True, null=True, help_text="List of work experiences")

    # Education
    educations = models.TextField(blank=True, null=True, help_text="List of educational qualifications")

    # Skills
    technical_skills = models.TextField(blank=True, null=True,
                                        help_text="List of technical skills")
    soft_skills = models.TextField(blank=True, null=True,
                                   help_text="List of soft skills")

    # Languages
    languages = models.TextField(blank=True, null=True,
                                 help_text="List of languages and proficiency levels")

    # Certifications
    certifications = models.TextField(blank=True, null=True, help_text="List of certifications")

    # Projects
    projects = models.TextField(blank=True, null=True, help_text="List of significant projects")

    # Volunteer Experience
    volunteer_experiences = models.TextField(blank=True, null=True,
                                             help_text="List of volunteer experiences")

    # Awards and Achievements
    awards = models.TextField(blank=True, null=True, help_text="List of awards and achievements")

    # Publications
    publications = models.TextField(blank=True, null=True, help_text="List of publications")

    # Professional Memberships
    memberships = models.TextField(blank=True, null=True, help_text="List of professional memberships")

    # Interests and Hobbies
    interests = models.TextField(blank=True, null=True,
                           help_text="List of interests and hobbies")

    # References
    references = models.TextField(blank=True, null=True, help_text="List of professional references")

    # Additional Information
    additional_info = models.TextField(blank=True, null=True,
                                       help_text="Any additional information relevant to the resume")

    # Metadata
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume v{self.version} for {self.candidate.First_Name} {self.candidate.Last_Name}"

    class Meta:
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"
        unique_together = ['candidate', 'version']
        ordering = ['-is_current', '-version']

    def save(self, *args, **kwargs):
        if self.is_current:
            # Set all other resumes of this candidate to not current
            Resume.objects.filter(candidate=self.candidate).update(is_current=False)
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)
