from django.db import models


class BookFile(models.Model):
    CLASS_ASSIGNMENT = (
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),

    )
    class_level = models.CharField(max_length=50, choices=CLASS_ASSIGNMENT, default='Not-Set')
    book_name = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    edition = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.class_level} - {self.book_name}"


class PdfMenschen(models.Model):
    book = models.ForeignKey(BookFile, on_delete=models.CASCADE, blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/')
    date_uploaded = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.book} - {self.pdf_file}"


class PdfGrammatik_Aktiv(models.Model):
    book = models.ForeignKey(BookFile, on_delete=models.CASCADE, blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/')
    date_uploaded = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.book} - {self.pdf_file}"


class PracticeMaterial(models.Model):
    description = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    date_uploaded = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.description} - {self.date_uploaded}"
