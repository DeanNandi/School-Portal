from django.urls import path
from . import views

urlpatterns = [
    path('video-menschen/', views.menschen_video, name='video-menschen'),
    path('download-video/', views.videos_view, name='download-video'),

]