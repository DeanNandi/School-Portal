from django.contrib import admin
from .models import PdfMenschen, BookFile, PdfGrammatik_Aktiv, PracticeMaterial


class PdfMenschenInline(admin.TabularInline):
    model = PdfMenschen
    extra = 1  # Number of empty forms to display


class PdfGrammatik_AktivInline(admin.TabularInline):
    model = PdfGrammatik_Aktiv
    extra = 1  # Number of empty forms to display


@admin.register(PdfGrammatik_Aktiv)
class PdfGrammatik_AktivAdmin(admin.ModelAdmin):
    list_display = ('get_book_name', 'pdf_file', 'date_uploaded')
    list_filter = ('book__book_name', 'date_uploaded')
    list_per_page = 10

    def get_book_name(self, obj):
        return f"{obj.book.class_level} {obj.book.book_name}"

    get_book_name.short_description = 'Book Name'


@admin.register(PdfMenschen)
class PdfMenschenAdmin(admin.ModelAdmin):
    list_display = ('get_book_name', 'pdf_file', 'date_uploaded')
    list_filter = ('book__book_name', 'date_uploaded')
    list_per_page = 10

    def get_book_name(self, obj):
        return f"{obj.book.class_level} {obj.book.book_name}"

    get_book_name.short_description = 'Book Name'


@admin.register(BookFile)
class BookFileAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'author', 'class_level')
    list_filter = ('book_name', 'author', 'class_level')
    list_per_page = 10

    # Add the inline for Transcripts
    inlines = [PdfMenschenInline, PdfGrammatik_AktivInline]


@admin.register(PracticeMaterial)
class PracticeMaterialAdmin(admin.ModelAdmin):
    list_display = ('description', 'link', 'date_uploaded')
    list_filter = ('description', 'date_uploaded')
    list_per_page = 10
