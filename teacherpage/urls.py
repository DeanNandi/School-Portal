from django.urls import path
from . import views

urlpatterns = [
    path('teacher-login/', views.loginTeacher, name="teacher-login"),
    path('teacher-logout/', views.logout_teacher, name="teacher-logout"),
    path('homepage/', views.teacher_landing_page, name="homepage"),
    path('classes/', views.classes, name="classes"),
    # New path for change_password view
    path('change-password/', views.change_password, name='change_password_url'),
    # Add the new path for toggling the pin status
    path('toggle-pin/<int:cohort_id>/', views.toggle_pin, name="toggle_pin"),
    path('examinations/', views.exam, name='examinations'),
    path('download-center/', views.library, name='download-center'),
]
