from django.urls import path
from . import views  # Import your views

# Ensure CSRF exemption is applied to endpoints that require it
urlpatterns = [
    path('crmpage/reports/', views.report_view, name='reports'),  # Existing report view
    path('reports_login/', views.reports_login_view, name='reports_login'),
    path('reports_logout/', views.reports_logout_view, name='reports_logout'),
    # Other relevant paths
    path('documents/info/', views.display_documents, name='display_documents'),  # Existing report view
    path('search-documents/', views.search_documents, name='search_documents'),
    path('display-teachers/', views.display_teachers, name='display_teachers'),
    path('payment-comparison/', views.payment_comparison, name='payment_comparison'),
    path('admin_attendance_dates/', views.admin_attendance_dates, name='admin_attendance_dates'),

]
