from django.contrib import admin
from .models import AudioMenschen, AudioFile, AudioGrammatik_Aktiv
from django.core.files.base import ContentFile
from zipfile import ZipFile
from io import BytesIO


class AudioMenschenInline(admin.TabularInline):
    model = AudioMenschen
    extra = 1  # Number of empty forms to display


class AudioGrammatik_AktivInline(admin.TabularInline):
    model = AudioGrammatik_Aktiv
    extra = 1  # Number of empty forms to display


@admin.register(AudioGrammatik_Aktiv)
class AudioGrammatik_AktivAdmin(admin.ModelAdmin):
    list_display = ('get_audio_name', 'zip_file', 'date_uploaded')
    list_filter = ('audio__audio_name', 'date_uploaded')
    list_per_page = 10

    def get_audio_name(self, obj):
        return f"{obj.audio.class_level} {obj.audio.audio_name}"

    get_audio_name.short_description = 'Audio Name'


@admin.register(AudioMenschen)
class AudioMenschenAdmin(admin.ModelAdmin):
    list_display = ('get_audio_name', 'zip_file', 'date_uploaded')
    list_filter = ('audio__audio_name', 'date_uploaded')
    list_per_page = 10

    def get_audio_name(self, obj):
        return f"{obj.audio.class_level} {obj.audio.audio_name}"

    get_audio_name.short_description = 'Audio Name'


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'audio_name')
    list_filter = ('class_level',)
    list_per_page = 10
    inlines = [AudioMenschenInline, AudioGrammatik_AktivInline]

    def save_model(self, request, obj, form, change):
        if 'zip_file' in request.FILES:
            zip_file = request.FILES['zip_file']
            zip_contents = BytesIO(zip_file.read())
            with ZipFile(zip_contents, 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    if file_name.endswith('.mp3') or file_name.endswith('.wav'):
                        file_content = zip_ref.read(file_name)
                        content_file = ContentFile(file_content)
                        if 'menschen' in file_name.lower():
                            audio_menschen = AudioMenschen(audio=obj)
                            audio_menschen.zip_file.save(file_name, content_file)
                        elif 'grammatik' in file_name.lower() or 'aktiv' in file_name.lower():
                            audio_grammatik_aktiv = AudioGrammatik_Aktiv(audio=obj)
                            audio_grammatik_aktiv.zip_file.save(file_name, content_file)
        super().save_model(request, obj, form, change)
