from django.urls import path
from . import views

urlpatterns = [
    path('audio-grammar/', views.grammar_audios, name='audio-grammar'),
    path('audio-menschen/', views.menschen_audio, name='audio-menschen'),
    path('download-audio/', views.audios_view, name='download-audio'),
    path('download-audio/<int:audio_id>/<path:file_path>/', views.download_audio, name='download_audio'),
    path('download-grammar-audio/<int:audio_id>/<path:file_path>/', views.download_grammar_audio, name='download_grammar_audio'),
]