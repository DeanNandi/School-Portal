from django.urls import path
from . import views

urlpatterns = [
    path('student-qr-codes/', views.student_qr_codes, name='student_qr_codes'),
    path('scan/<int:candidate_id>/', views.scan_qr_code, name='scan_qr_code'),
    path('scan/success/<int:scan_id>/', views.scan_success, name='scan_success'),
    #  New Authentication URLs
    path('qr-scanner-login/', views.qr_scanner_login, name='qr_scanner_login'),
    path('qr-scanner-logout/', views.qr_scanner_logout, name='qr_scanner_logout'),
]
