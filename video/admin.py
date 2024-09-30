from django.contrib import admin
from .models import VideoMenschen, VideoFile


class VideoMenschenInline(admin.TabularInline):
    model = VideoMenschen
    extra = 1  # Number of empty forms to display


@admin.register(VideoMenschen)
class VideoMenschenAdmin(admin.ModelAdmin):
    list_display = ('get_video_name', 'video_file', 'date_uploaded')
    list_filter = ('video__video_name', 'date_uploaded')
    list_per_page = 10

    def get_video_name(self, obj):
        return f"{obj.video.class_level} {obj.video.video_name}"

    get_video_name.short_description = 'Video Name'


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('class_level', 'video_name')
    list_filter = ('class_level',)
    list_per_page = 10

    # Add the inline for Transcripts
    inlines = [VideoMenschenInline]
