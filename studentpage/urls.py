from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('upload-documents/', views.upload_documents, name='upload_documents'),  # URL pattern for document uploads
    path('delete_transcript/<int:transcript_id>/', views.delete_transcript, name='delete_transcript'),
    # Example URL configuration
    path('delete-document/', views.delete_document, name='delete_document'),
    path('coursework/', views.coursework, name='coursework'),
    path('class_attendance/', views.attendance, name='class-attendance'),
    path('payment_history/', views.payments, name='payment-history'),
    path('downloads/', views.download_view, name='downloads'),
    # New path for change_password view
    path('change-password/', views.change_password, name='change_password_url'),
    # New imports
    path('import-candidates/', views.import_candidates_view, name='import-candidates'),
    # serializers.py
    path('api/candidate/', views.CandidateCreateAPI.as_view(), name='create_candidate'),
    # New URL patterns for device registration and student dashboard
    path('wifi-login/', views.wifi_login, name='wifi_login'),
    path('update-device/', views.update_device, name='update_device'),
    path('remove-device/', views.remove_device, name='remove_device'),
    # New URL patterns for device registration and student dashboard
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('password_reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    # resume builder
    path('resume-builder/', views.resume_builder, name='resume_builder'),
    path('resume-preview/', views.resume_preview, name='resume_preview'),
    path('generate-pdf-resume/', views.generate_pdf_resume, name='generate_pdf_resume'),
    # New URL pattern for resume management
    path('manage-resume/', views.manage_resume, name='manage_resume'),
    path('generate-resume-preview/', views.generate_resume_preview, name='generate_resume_preview'),

]
