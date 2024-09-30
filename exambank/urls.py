from django.urls import path
from . import views

urlpatterns = [
    path('exam-menschen/', views.menschen_exam, name='exam-menschen'),
    path('download-exam/', views.exams_view, name='download-exam'),

]