from django.urls import path
from . import views

urlpatterns = [
    path('class_attendance/', views.class_attendance_record, name='class_attendance_record'),
    path('attendance-details/<int:candidate_id>/', views.attendance_details, name='attendance_details'),
    # modify existing attendance
    path('edit_attendance/<str:date>/', views.edit_class_attendance, name='edit_class_attendance'),
    path('attendance/dates/', views.list_attendance_dates, name='list_attendance_dates'),
    path('delete_attendance/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
    # New path for downloading candidates as PDF
    path('download-candidates/', views.download_candidate_list_pdf, name='download_candidates_pdf'),
    # reports
    path('attendance/overview/', views.attendance_overview, name='attendance_overview'),
    path('display_attendance/', views.display_attendance, name='display_attendance'),
    # filter students
    path('filter-students/', views.filter_candidates, name='filter_candidates'),
    # viewing attendance
    path('attendance-date-picker/', views.attendance_date_picker, name='attendance_date_picker'),
    path('view-attendance/<str:start_date>/<str:end_date>/', views.view_attendance, name='view_attendance'),
]
