from django.shortcuts import render, redirect, get_object_or_404
from .models import ClassAttendance
from studentpage.models import Candidate
from teacherpage.models import Cohort
from django.contrib.auth.decorators import login_required
from .forms import ClassAttendanceForm
from django.db.models import F

# display attendance reports
import calendar
import urllib.parse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Refactor students' Attendance Records
from django.db.models import Q
from collections import defaultdict
from django.utils import timezone

# download attendance
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, Image
from reportlab.lib.pagesizes import landscape, legal
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus.tables import TableStyle, LongTable

# Displaying Attendance
from collections import Counter
from django.db.models import Count, Case, When
from django.db.models.functions import TruncDate

# Modify existing attendance
from django.contrib import messages

# For attendance reports
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.contrib.auth import get_user_model
from teacherpage.models import Teacher


@login_required
def attendance_date_picker(request):
    # Get the earliest and latest attendance dates for the current user
    earliest_date = ClassAttendance.objects.filter(user=request.user).order_by('date').first()
    latest_date = ClassAttendance.objects.filter(user=request.user).order_by('-date').first()

    context = {
        'earliest_date': earliest_date.date if earliest_date else timezone.now().date(),
        'latest_date': latest_date.date if latest_date else timezone.now().date(),
    }

    return render(request, 'attendance_date_picker.html', context)


@login_required
def teacher_attendance_dates(request):
    # Get distinct dates along with user information, filtering by the current user
    dates_with_users = (ClassAttendance.objects.filter(user=request.user)
                        .annotate(date_str=F('date'), username=F('user__username'))
                        .values('date_str', 'username')
                        .distinct()
                        .order_by('-date_str'))

    # Organize data for display, grouping records by date
    organized_data = {}
    for record in dates_with_users:
        date = record['date_str']
        username = record['username']
        if date not in organized_data:
            organized_data[date] = [username]
        elif username not in organized_data[date]:
            organized_data[date].append(username)

    return render(request, 'teacher_attendance_dates.html', {'organized_data': organized_data})


@login_required
def view_attendance(request, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    attendance_records = ClassAttendance.objects.filter(
        date__range=[start_date, end_date],
        user=request.user
    ).select_related('candidate')

    total_students = attendance_records.values('candidate').distinct().count()
    total_classes = attendance_records.values('date').distinct().count()

    # Calculate student-wise attendance summary
    student_summary = attendance_records.values('candidate__First_Name', 'candidate__Last_Name') \
        .annotate(
        present_days=Count(Case(When(present=True, then=1))),
        absent_days=Count(Case(When(present=False, then=1)))
    )

    student_attendance_summary = []
    for student in student_summary:
        total_days = student['present_days'] + student['absent_days']
        attendance_rate = (student['present_days'] / total_days) * 100 if total_days > 0 else 0

        # Get absence reasons and their counts
        absence_reasons = attendance_records.filter(
            candidate__First_Name=student['candidate__First_Name'],
            candidate__Last_Name=student['candidate__Last_Name'],
            present=False
        ).values('absent_reason').annotate(count=Count('absent_reason')).order_by('-count')

        most_common_reason = absence_reasons.first()['absent_reason'] if absence_reasons else None

        # Calculate absence trend
        recent_absences = attendance_records.filter(
            candidate__First_Name=student['candidate__First_Name'],
            candidate__Last_Name=student['candidate__Last_Name'],
            present=False,
            date__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        previous_absences = attendance_records.filter(
            candidate__First_Name=student['candidate__First_Name'],
            candidate__Last_Name=student['candidate__Last_Name'],
            present=False,
            date__lt=timezone.now() - timezone.timedelta(days=30),
            date__gte=timezone.now() - timezone.timedelta(days=60)
        ).count()
        absence_trend = recent_absences - previous_absences

        # Get last absence date
        last_absence = attendance_records.filter(
            candidate__First_Name=student['candidate__First_Name'],
            candidate__Last_Name=student['candidate__Last_Name'],
            present=False
        ).order_by('-date').first()

        student_attendance_summary.append({
            'name': f"{student['candidate__First_Name']} {student['candidate__Last_Name']}",
            'present_days': student['present_days'],
            'absent_days': student['absent_days'],
            'attendance_rate': attendance_rate,
            'most_common_reason': most_common_reason,
            'absence_reasons': {reason['absent_reason']: reason['count'] for reason in absence_reasons},
            'absence_trend': absence_trend,
            'last_absence_date': last_absence.date if last_absence else None,
            'reason_class': get_reason_class(most_common_reason)
        })

    # Calculate average attendance rate
    average_attendance_rate = sum(student['attendance_rate'] for student in student_attendance_summary) / len(
        student_attendance_summary) if student_attendance_summary else 0

    # Get most common absence reasons
    all_reasons = attendance_records.filter(present=False).values_list('absent_reason', flat=True)
    common_absence_reasons = Counter(all_reasons).most_common(3)

    # Prepare data for attendance trend chart
    attendance_by_date = attendance_records.annotate(trunc_date=TruncDate('date')) \
        .values('trunc_date') \
        .annotate(
        present_count=Count(Case(When(present=True, then=1))),
        total_count=Count('id')
    )

    date_labels = [record['trunc_date'].strftime('%Y-%m-%d') for record in attendance_by_date]
    attendance_rates = [
        (record['present_count'] / record['total_count']) * 100
        for record in attendance_by_date
    ]

    # Prepare daily attendance records
    daily_attendance_records = {}
    for record in attendance_records.order_by('date', 'candidate__First_Name'):
        date_str = record.date.strftime('%Y-%m-%d')
        if date_str not in daily_attendance_records:
            daily_attendance_records[date_str] = []

        daily_attendance_records[date_str].append({
            'student_name': f"{record.candidate.First_Name} {record.candidate.Last_Name}",
            'status': 'Present' if record.present else 'Absent',
            'reason': record.absent_reason if not record.present else 'N/A'
        })

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_students': total_students,
        'total_classes': total_classes,
        'average_attendance_rate': average_attendance_rate,
        'student_attendance_summary': student_attendance_summary,
        'common_absence_reasons': common_absence_reasons,
        'date_labels': date_labels,
        'attendance_rates': attendance_rates,
        'daily_attendance_records': daily_attendance_records,
    }

    return render(request, 'view_attendance.html', context)


def get_reason_class(reason):
    reason_classes = {
        'Too Late': 'reason-late',
        'Absent with Excuse': 'reason-excused',
        'Absent without Excuse': 'reason-unexcused',
    }
    return reason_classes.get(reason, 'reason-other')


@login_required(login_url='/teacher-login/')
def download_candidate_list_pdf(request):
    cohort_id = request.GET.get('cohort_id')
    selected_time = request.GET.get('time')
    cohort = get_object_or_404(Cohort, id=cohort_id) if cohort_id else None
    teacher = request.user.teacher if request.user.is_authenticated and hasattr(request.user, 'teacher') else None
    teacher_course_location = teacher.course_location if teacher else None

    candidates = Candidate.objects.filter(
        course_intake=cohort.course_intake,
        Course_Location=teacher_course_location
    ) if cohort and teacher_course_location else Candidate.objects.none()

    if selected_time:
        candidates = candidates.filter(Time=selected_time)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{datetime.now().date()}-Attendance.pdf"'
    doc = SimpleDocTemplate(response, pagesize=landscape(legal))

    logo_path = '/home/AgCrm/Agschool/static/img/AG_German_Institute.png'
    logo = Image(logo_path, width=200, height=30)
    logo.hAlign = 'CENTER'

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # Center alignment

    def create_overview_table():
        overview_data = [
            ['Date Printed:', datetime.now().strftime('%Y-%m-%d'), 'Teacher:',
             teacher.user.username if teacher else 'N/A'],
            ['Course Intake:', cohort.course_intake.course_intake if cohort else 'N/A', 'Course Location:',
             teacher_course_location if teacher_course_location else 'N/A']
        ]
        overview_table = Table(overview_data, colWidths=[120, 180, 120, 180], spaceBefore=20, spaceAfter=20)
        overview_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        overview_table.setStyle(overview_style)
        return overview_table

    elements = []

    class PageNumCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self.pages = []

        def showPage(self):
            self.pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            page_count = len(self.pages)
            for page in self.pages:
                self.__dict__.update(page)
                self.draw_page_number(page_count)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            page = f"Page {self._pageNumber} of {page_count}"
            self.setFont("Helvetica", 9)
            self.drawRightString(11 * inch, 0.75 * inch, page)

    elements.append(logo)
    elements.append(create_overview_table())

    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']
    subheaders = ['STUDENTS'] + [f'{day}' for day in days for _ in (0, 1)]
    headers = [''] + ['Tick if Present', 'Signature'] * len(days)

    first_column_width = 180
    subsequent_column_widths = [80, 80]
    column_widths = [first_column_width] + subsequent_column_widths * len(days)

    attendance_data = [subheaders, headers] + [
        [candidate.First_Name + " " + candidate.Last_Name] + ['' for _ in range(len(days) * 2)] for candidate in
        candidates
    ]

    attendance_table = LongTable(attendance_data, colWidths=column_widths, repeatRows=2)

    attendance_style = TableStyle([
                                      ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                      ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                      ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                      ('TOPPADDING', (0, 0), (-1, -1), 8),
                                      ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                  ] + [
                                      ('SPAN', (i, 0), (i + 1, 0)) for i in range(1, len(subheaders) - 1, 2)
                                  ] + [
                                      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                      ('FONTSIZE', (0, 0), (-1, 0), 15),
                                      ('FONTNAME', (1, 1), (-1, 1), 'Helvetica'),
                                      ('FONTSIZE', (1, 1), (-1, 1), 10)
                                  ])
    attendance_table.setStyle(attendance_style)

    elements.append(attendance_table)

    doc.build(elements, onFirstPage=PageNumCanvas, onLaterPages=PageNumCanvas)

    return response


@login_required(login_url='/teacher-login/')
def filter_candidates(request):
    cohort_id = request.GET.get('cohort_id')
    cohort = get_object_or_404(Cohort, id=cohort_id)
    time_choices = Candidate._meta.get_field('Time').choices

    context = {
        'cohort': cohort,
        'time_choices': time_choices,
    }
    return render(request, 'filter_candidates.html', context)


@login_required(login_url='login')
def attendance_details(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate

    attendances = ClassAttendance.objects.filter(candidate=candidate).order_by('-date')
    total_classes = attendances.count()
    days_present = attendances.filter(present=True).count()
    days_absent = attendances.filter(Q(present=False) & Q(absent_reason__isnull=False)).count()

    # Group attendances by month
    monthly_attendances = defaultdict(list)
    for attendance in attendances:
        month_key = attendance.date.strftime("%Y-%m")
        monthly_attendances[month_key].append(attendance)

    # Calculate monthly statistics
    monthly_stats = []
    for month, month_attendances in monthly_attendances.items():
        month_total = len(month_attendances)
        month_present = sum(1 for a in month_attendances if a.present)
        month_absent = month_total - month_present
        month_date = timezone.datetime.strptime(month, "%Y-%m")

        monthly_stats.append({
            'month': month_date.strftime("%B %Y"),
            'total_classes': month_total,
            'days_present': month_present,
            'days_absent': month_absent,
            'attendances': month_attendances
        })

    context = {
        'candidate': candidate,
        'monthly_stats': monthly_stats,
        'total_classes': total_classes,
        'days_present': days_present,
        'days_absent': days_absent,
    }
    return render(request, 'attendance_details.html', context)


def attendance_overview(request):
    # Decode and clean the 'course_intake' and 'Course_Location' parameters from the request
    course_intake_encoded = request.GET.get('course_intake')
    course_location_encoded = request.GET.get('Course_Location')

    course_intake = urllib.parse.unquote(course_intake_encoded) if course_intake_encoded else None
    course_location = urllib.parse.unquote(course_location_encoded).strip() if course_location_encoded else None

    # Retrieve all cohorts
    cohorts = Cohort.objects.all()

    # Filter cohorts based on the provided 'course_intake'
    if course_intake:
        cohorts = cohorts.filter(course_intake=course_intake)

    # Filter cohorts based on the provided 'Course_Location'
    if course_location:
        cohorts = cohorts.filter(teacher__course_location=course_location)

    # Obtain unique class numbers for navigation or display purposes
    unique_class_numbers = cohorts.order_by('course_class_no').values_list('course_class_no', flat=True).distinct()

    # Group teachers by course class number, location, and intake
    class_groups_by_location = {}
    for cohort in cohorts:
        location = cohort.teacher.course_location
        class_no = cohort.course_class_no

        if location not in class_groups_by_location:
            class_groups_by_location[location] = {}

        if class_no not in class_groups_by_location[location]:
            class_groups_by_location[location][class_no] = {
                'teachers': set(),
                'course_intake': cohort.course_intake,
                'Course_Location': location  # Ensure to store location as part of each class group
            }

        class_groups_by_location[location][class_no]['teachers'].add(
            f"{cohort.teacher.first_name} {cohort.teacher.last_name}"
        )

    # Convert sets of teacher names to comma-separated strings
    for location, class_info in class_groups_by_location.items():
        for class_no, info in class_info.items():
            info['teachers'] = ', '.join(info['teachers'])

    # Prepare context for rendering the template
    context = {
        'class_groups_by_location': class_groups_by_location,
        'unique_class_numbers': unique_class_numbers,
        'course_intake': course_intake,
        'course_location': course_location,
    }

    return render(request, 'reports_overview.html', context)


def display_attendance(request):
    # Get parameters from request
    course_intake = request.GET.get('course_intake')
    course_location = request.GET.get('Course_Location')
    selected_date_str = request.GET.get('selected_date')

    # Parse the selected date or use today's date
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = datetime.now().date()

    # Calculate the date range (1 week)
    # Note: This is kept for potential future use or if you need to limit the date range
    start_date = selected_date - timedelta(days=selected_date.weekday())
    end_date = start_date + timedelta(days=6)

    # Get candidates
    candidates = Candidate.objects.filter(course_intake=course_intake)
    if course_location:
        candidates = candidates.filter(Course_Location=course_location)

    # Get the total number of classes
    total_classes = ClassAttendance.objects.filter(
        candidate__course_intake=course_intake
    ).values('date').distinct().count()

    # New: Get teachers who have added attendance data
    teacher_data = ClassAttendance.objects.filter(
        candidate__course_intake=course_intake
    ).values('user').annotate(
        records_count=Count('id')
    ).order_by('-records_count')

    # Get attendance for all dates
    attendance_data = []
    for candidate in candidates:
        # Fetch all attendance records for the candidate
        attendances = ClassAttendance.objects.filter(candidate=candidate)

        # Calculate summary statistics
        total_records = attendances.count()
        present_count = attendances.filter(present=True).count()
        absent_count = total_records - present_count

        # Calculate attendance percentage based on total_classes
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

        # Store summary data
        attendance_data.append({
            'candidate': candidate,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_percentage': attendance_percentage,
            'total_records': total_records,  # Kept for potential future use
        })

    # New: Process teacher data
    User = get_user_model()
    teachers_info = []
    for data in teacher_data:
        user = User.objects.filter(id=data['user']).first()
        if user:
            try:
                teacher = Teacher.objects.get(user=user)
                teachers_info.append({
                    'name': f"{teacher.first_name} {teacher.last_name}",
                    'records_count': data['records_count'],
                    'course_location': teacher.course_location
                })
            except Teacher.DoesNotExist:
                # Handle cases where User exists but Teacher doesn't
                teachers_info.append({
                    'name': f"User {user.username}",
                    'records_count': data['records_count'],
                    'course_location': 'Unknown'
                })

    # Prepare context for the template
    context = {
        'attendance_data': attendance_data,
        'selected_date': selected_date,  # Kept for potential future use
        'start_date': start_date,  # Kept for potential future use
        'end_date': end_date,  # Kept for potential future use
        'course_intake': course_intake,
        'course_location': course_location,
        'total_classes': total_classes,
        'teachers_info': teachers_info,  # New: Added teacher information
    }

    return render(request, 'display_attendance.html', context)


@login_required(login_url='/teacher-login/')
def class_attendance_record(request):
    thank_you_message = None
    # Retrieve the cohort_id from the GET parameters.
    cohort_id = request.GET.get('cohort_id')
    cohort = get_object_or_404(Cohort, id=cohort_id) if cohort_id else None

    # Retrieve the selected time from the GET parameters.
    selected_time = request.GET.get('time')

    # Retrieve the current logged-in teacher's course location.
    teacher_course_location = None
    if request.user.is_authenticated and hasattr(request.user, 'teacher'):
        teacher_course_location = request.user.teacher.course_location

    if cohort and teacher_course_location:
        # Filter candidates by the selected cohort and the teacher's course location.
        candidates = Candidate.objects.filter(
            course_intake=cohort.course_intake,
            Course_Location=teacher_course_location
        )

        # Filter candidates based on the selected time, if provided.
        if selected_time:
            candidates = candidates.filter(Time=selected_time)
    else:
        candidates = Candidate.objects.none()

    # Get choices for the 'absent_reason' field from the ClassAttendance model.
    absent_reason_choices = ClassAttendance._meta.get_field('absent_reason').choices

    # Get choices for the 'Time' field from the Candidate model.
    time_choices = Candidate._meta.get_field('Time').choices

    if request.method == 'POST':
        # Process the attendance form submission.
        date = request.POST.get('date')
        for candidate in candidates:
            present_key = f'present_{candidate.id}'
            absent_reason_key = f'absent_reason_{candidate.id}'
            present = request.POST.get(present_key) == 'on'
            absent_reason = request.POST.get(absent_reason_key)
            # Only create or update the attendance record if present or absent_reason is provided.
            if present or absent_reason:
                ClassAttendance.objects.update_or_create(
                    candidate=candidate,
                    date=date,
                    defaults={'present': present, 'absent_reason': absent_reason, 'user': request.user},
                )
        thank_you_message = "Attendance Captured! Do you want to make another submission?"

    context = {
        'thank_you_message': thank_you_message,
        'candidates': candidates,
        'cohort': cohort,
        'absent_reason_choices': absent_reason_choices,
        'time_choices': time_choices,
        'selected_time': selected_time,
    }
    return render(request, 'class_attendance.html', context)


@login_required(login_url='/teacher-login/')
def edit_class_attendance(request, date):
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    formatted_date = date_obj.strftime('%A, %B %d, %Y')

    attendance_records = ClassAttendance.objects.filter(date=date_obj, user=request.user)

    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        if record_id:
            record = get_object_or_404(ClassAttendance, id=record_id, user=request.user)
            form = ClassAttendanceForm(request.POST, instance=record, prefix=str(record_id))

            if form.is_valid():
                attendance = form.save(commit=False)
                attendance.date = date_obj
                attendance.save()
                messages.success(request,
                                 f"Attendance record for {record.candidate.First_Name} {record.candidate.Last_Name} updated successfully.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request,
                                       f"Error updating attendance record for {record.candidate.First_Name} {record.candidate.Last_Name}: {error}")
        return redirect('edit_class_attendance', date=date)

    forms = []
    for record in attendance_records:
        form = ClassAttendanceForm(instance=record, prefix=str(record.id))
        forms.append((record, form))

    return render(request, 'edit_class_attendance.html', {
        'attendance_forms': forms,
        'date': date,
        'formatted_date': formatted_date,
    })


@login_required
def delete_attendance(request, attendance_id):
    attendance_record = get_object_or_404(ClassAttendance, id=attendance_id)
    attendance_date = attendance_record.date  # Extract the date before deletion

    if request.method == 'POST':
        attendance_record.delete()
        # Convert the date to string format expected by the URL
        date_str = datetime.strftime(attendance_date, '%Y-%m-%d')
        # Redirect to the edit_class_attendance view for the same date
        return redirect('edit_class_attendance', date=date_str)
    else:
        # Show a simple confirmation page for GET requests
        return render(request, 'confirm_delete.html', {'attendance_record': attendance_record})


@login_required
def list_attendance_dates(request):
    # Get distinct dates along with user information, filtering by the current user
    dates_with_users = (ClassAttendance.objects.filter(user=request.user)
                        .annotate(date_str=F('date'), username=F('user__username'))
                        .values('date_str', 'username')
                        .distinct()
                        .order_by('-date_str'))

    # Organize data for display, grouping records by date
    organized_data = {}
    for record in dates_with_users:
        date = record['date_str']
        username = record['username']
        if date not in organized_data:
            organized_data[date] = [username]
        elif username not in organized_data[date]:
            organized_data[date].append(username)

    return render(request, 'list_attendance_dates.html', {'organized_data': organized_data})


def admin_attendance_dates(request):
    # Get distinct dates along with user information
    dates_with_users = (ClassAttendance.objects
                        .annotate(date_str=F('date'), username=F('user__username'))
                        .values('date_str', 'username')
                        .distinct()
                        .order_by('-date_str'))

    # Optional: Organize data for display, e.g., by grouping records by date
    organized_data = {}
    for record in dates_with_users:
        date = record['date_str']
        username = record['username']
        if date not in organized_data:
            organized_data[date] = [username]
        elif username not in organized_data[date]:
            organized_data[date].append(username)

    return render(request, 'admin_attendance.html', {'organized_data': organized_data})
