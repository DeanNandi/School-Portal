from django.shortcuts import render, redirect, get_object_or_404
from studentpage.models import Candidate
from django.contrib.auth.decorators import login_required
from .forms import ExaminationForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

# download exam results for students
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from reportlab.lib.units import inch

# New Reports Data
from teacherpage.models import Cohort, CourseIntake, Teacher
from .models import Examination, StudentExam, ExaminationReport
from django.db.models import Exists
from django.db.models import OuterRef, F

# managing students
import logging

# New Assessments Capturing
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.db.models import Count, Q, Subquery, Prefetch
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST
from django.db import transaction
from django.http import JsonResponse
from .models import ClassReport, ScheduledExam

logger = logging.getLogger(__name__)


@login_required(login_url='/login/')
def download_exam_results_pdf(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate

    exams = StudentExam.objects.filter(student=candidate)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    def draw_page_header(p):
        # Logo
        logo_path = 'C:/Users/Dell/PycharmProjects/agCrm/crmpage/static/img/AG_German_Institute.png'
        p.drawImage(logo_path, width - 2.5 * inch, height - 1 * inch, width=1.5 * inch, height=0.75 * inch,
                    preserveAspectRatio=True)

        # School details
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, height - 1 * inch, "AG German School Ltd.")
        p.setFont("Helvetica", 10)
        p.drawString(1 * inch, height - 1.2 * inch, "Ambank House")
        p.drawString(1 * inch, height - 1.4 * inch, "00100 CBD, Nairobi")

        # Date and admission number
        today_date = datetime.today().strftime('%Y-%m-%d')
        p.drawString(width - 3 * inch, height - 1.8 * inch, f"Date Generated: {today_date}")
        p.drawString(width - 3 * inch, height - 2 * inch, f"Admission Number: {candidate.admission_number}")

        # Student name
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1 * inch, height - 2.5 * inch,
                     f"Assessment Results for: {candidate.First_Name} {candidate.Last_Name}")

        # Table Headers
        headers = ["Assessment", "Average", "Speaking", "Listening", "Reading", "Writing"]
        x_positions = [1 * inch, 5 * inch, 6.5 * inch, 7.5 * inch, 8.5 * inch, 9.5 * inch]
        header_y = height - 3 * inch

        p.setFont("Helvetica-Bold", 12)
        for i, header in enumerate(headers):
            p.drawString(x_positions[i], header_y, header)

        # Draw horizontal line below headers
        p.line(1 * inch, header_y - 0.1 * inch, width - 1 * inch, header_y - 0.1 * inch)

        return header_y - 0.5 * inch

    def wrap_text(text, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            if p.stringWidth(' '.join(current_line + [word]), "Helvetica", 10) <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines

    def center_text(pdf, text, y):
        text_width = pdf.stringWidth(text, "Helvetica", 8)
        centered_x = (width - text_width) / 2
        pdf.drawString(centered_x, y, text)

    def draw_footer(p):
        footer_lines = [
            "Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi.",
            "Phone and WhatsApp +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke",
            "Kenya Commercial Bank - Account number 1321761716 or MPESA Paybill: 522 533 Account No: 774 5020.",
            "Thank you for being part of our Institution."
        ]

        footer_height = len(footer_lines) * 0.2 * inch
        footer_start_y = 1 * inch  # Start 1 inch from bottom

        p.setFont("Helvetica", 8)
        for i, line in enumerate(footer_lines):
            center_text(p, line, footer_start_y + (len(footer_lines) - 1 - i) * 0.2 * inch)

        return footer_height + footer_start_y

    def new_page():
        p.showPage()
        return draw_page_header(p)

    def draw_score(p, x, y, score, total):
        if score is not None and total is not None:
            p.drawString(x, y, f"{score} / {total}")
        else:
            p.drawString(x, y, 'N/A')

    y_position = draw_page_header(p)
    footer_top = draw_footer(p)

    p.setFont("Helvetica", 10)
    for exam in exams:
        exam_name = exam.name_of_exam.examination_name if exam.name_of_exam.examination_name else exam.name_of_exam.class_level
        wrapped_name = wrap_text(exam_name, 3.5 * inch)

        entry_height = max(0.6 * inch, len(wrapped_name) * 0.2 * inch)

        if y_position - entry_height < footer_top:
            y_position = new_page()
            footer_top = draw_footer(p)

        for i, line in enumerate(wrapped_name):
            p.drawString(1 * inch, y_position - i * 0.2 * inch, line)

        # Draw scores with subtotals
        p.drawString(5 * inch, y_position, str(exam.percentage_score or 'N/A'))
        draw_score(p, 6.5 * inch, y_position, exam.speaking_score, exam.speaking_total)
        draw_score(p, 7.5 * inch, y_position, exam.listening_score, exam.listening_total)
        draw_score(p, 8.5 * inch, y_position, exam.reading_score, exam.reading_total)
        draw_score(p, 9.5 * inch, y_position, exam.writing_score, exam.writing_total)

        y_position -= entry_height

    p.save()
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response[
        'Content-Disposition'] = f'attachment; filename="{candidate.First_Name}-{candidate.Last_Name}_assessments.pdf"'
    return response


# Coming soon
@login_required(login_url='/teacher-login/')
def exam_class_numbers(request):
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        cohorts = Cohort.objects.filter(teacher=teacher).order_by('course_class_no').select_related('course_intake')
        unique_class_numbers = [(cohort.course_class_no, str(cohort.course_intake)) for cohort in cohorts]
    else:
        unique_class_numbers = []

    context = {
        'unique_class_numbers': unique_class_numbers,
    }
    return render(request, 'exams_filter_with_class.html', context)


@login_required(login_url='/teacher-login/')
def reports_existing_exams(request):
    course_class_no = request.GET.get('course_class_no')
    if course_class_no:
        examinations = Examination.objects.filter(class_information__course_class_no=course_class_no)
    else:
        examinations = Examination.objects.all()

    exam_data = []
    for exam in examinations.select_related('class_information__teacher'):
        scheduled_exam = ScheduledExam.objects.filter(user=request.user, examination=exam).first()
        exam_data.append({
            'exam': exam,
            'scheduled_date': scheduled_exam.scheduled_date if scheduled_exam else None
        })

    context = {
        'exam_data': exam_data,
    }
    return render(request, 'reports_existing_exams.html', context)


@login_required(login_url='/teacher-login/')
def filter_students_for_reports(request, exam_id):
    examination = get_object_or_404(Examination, id=exam_id)
    course_class_no = request.GET.get('course_class_no')

    if not course_class_no:
        messages.error(request, "No class number provided. Please select a valid class number.")
        return redirect('exam_class_numbers')

    cohort = Cohort.objects.filter(course_class_no=course_class_no).first()

    time_choices = dict(Candidate._meta.get_field('Time').choices)
    time_choices = {k: v for k, v in time_choices.items() if k is not None}
    current_time_filter = request.GET.get('time_filter')

    context = {
        'examination': examination,
        'cohort': cohort,
        'time_choices': time_choices,
        'current_time_filter': current_time_filter,
        'course_class_no': course_class_no,
    }

    if not cohort:
        messages.warning(request,
                         f"No cohort found with class number: {course_class_no}. Please select a valid class number.")
        return redirect('exam_class_numbers')
    elif current_time_filter:
        return redirect(reverse('manage_examination_reports', kwargs={'exam_id': exam_id}) +
                        f'?course_class_no={course_class_no}&time_filter={current_time_filter}')

    return render(request, 'filter_students_for_reports.html', context)


@login_required(login_url='/teacher-login/')
def manage_examination_reports(request, exam_id):
    examination = get_object_or_404(Examination, id=exam_id)
    course_class_no = request.GET.get('course_class_no') or request.POST.get('course_class_no')
    time_filter = request.GET.get('time_filter') or request.POST.get('time_filter')

    # Only redirect if it's a GET request and there's no time filter
    if request.method == "GET" and not time_filter:
        return redirect(reverse('filter_students_for_reports', kwargs={'exam_id': exam_id}) +
                        f'?course_class_no={course_class_no}')

    # Retrieve the current logged-in teacher's course location.
    teacher = get_object_or_404(Teacher, user=request.user)
    teacher_course_location = teacher.course_location

    cohorts = Cohort.objects.filter(course_class_no=course_class_no)

    if cohorts.exists():
        cohort = cohorts.first()
        students = Candidate.objects.filter(
            course_intake=cohort.course_intake,
            Time=time_filter,
            Course_Location=teacher_course_location
        )
    else:
        messages.error(request, f"No cohort found with class number: {course_class_no}")
        return redirect('exam_class_numbers')

    # Fetch all student exams for this examination and these students
    student_exams = StudentExam.objects.filter(
        name_of_exam=examination,
        student__in=students
    ).select_related('student', 'examination_report')

    if not student_exams.exists():
        messages.warning(request,
                         f"No student exams found for the given criteria: Class {course_class_no}, Time {time_filter}")
        return redirect(reverse('filter_students_for_reports', kwargs={'exam_id': exam_id}) +
                        f'?course_class_no={course_class_no}')

    # Get or create ExaminationReports for each StudentExam
    examination_reports = []
    for student_exam in student_exams:
        report, created = ExaminationReport.objects.get_or_create(
            student_exam=student_exam,
            candidate=student_exam.student,
            teacher=teacher
        )
        examination_reports.append(report)

    # Get or create ClassReport for this examination and cohort
    class_report, created = ClassReport.objects.get_or_create(
        examination=examination,
        cohort=cohort
    )

    if request.method == 'POST':
        if 'overall_report' in request.POST:
            # Handle the overall class report update
            overall_report = request.POST.get('overall_report', '').strip()
            class_report.overall_report = overall_report
            class_report.save()

            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Overall report updated successfully',
                })
        else:
            # Handle individual student report updates
            return update_examination_report(request, student_exams, examination_reports)

    context = {
        'examination': examination,
        'cohort': cohort,
        'student_exams': student_exams,
        'examination_reports': examination_reports,
        'way_forward_choices': ExaminationReport.WAY_FORWARD_CHOICES,
        'course_class_no': course_class_no,
        'time_filter': time_filter,
        'teacher': teacher,
        'class_report': class_report,  # Add class_report to the context
    }
    return render(request, 'manage_examination_reports.html', context)


@require_POST
def update_examination_report(request, student_exam_id):
    try:
        with transaction.atomic():
            student_exam = get_object_or_404(StudentExam, id=student_exam_id)

            # Get or create the examination report
            examination_report, created = ExaminationReport.objects.get_or_create(
                student_exam=student_exam,
                defaults={
                    'candidate': student_exam.student,
                    'teacher': student_exam.user.teacher  # Assuming the user associated with StudentExam is a teacher
                }
            )

            teachers_notes = request.POST.get('teachers_notes', '').strip()
            way_forward = request.POST.get('way_forward', '').strip()

            logger.info(f"Updating report for student_exam_id: {student_exam_id}")
            logger.info(f"Received teachers_notes: {teachers_notes}")
            logger.info(f"Received way_forward: {way_forward}")

            examination_report.teachers_notes = teachers_notes
            examination_report.way_forward = way_forward
            examination_report.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Examination report updated successfully',
        })
    except Exception as e:
        logger.exception(f"Error updating examination report for student_exam_id: {student_exam_id}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)  # Return the actual error message for debugging
        }, status=500)


def get_adjacent_levels(current_level):
    levels = ['A1.1', 'A1.2', 'A2.1', 'A2.2', 'B1.1', 'B1.2', 'B2.1', 'B2.2']
    if current_level not in levels:
        return None, None
    current_index = levels.index(current_level)
    previous_level = levels[current_index - 1] if current_index > 0 else None
    next_level = levels[current_index + 1] if current_index < len(levels) - 1 else None
    return previous_level, next_level


from django.db.models import Count, Q, F, Value as V, Subquery, OuterRef
from django.db.models.functions import Concat


def assessments_view(request):
    # Start with all student exams
    student_exams = StudentExam.objects.select_related(
        'name_of_exam__class_information__teacher',
        'name_of_exam__class_information__course_intake',
        'user',
        'student'
    ).annotate(
        added_by_name=Concat('user__first_name', V(' '), 'user__last_name'),
        added_by_id=F('user__id'),
        course_intake=F('name_of_exam__class_information__course_intake__course_intake'),
        class_no=F('name_of_exam__class_information__course_class_no'),
        teacher_first_name=F('name_of_exam__class_information__teacher__first_name'),
        teacher_last_name=F('name_of_exam__class_information__teacher__last_name'),
        teacher_id=F('name_of_exam__class_information__teacher__id'),
        teacher_location=F('name_of_exam__class_information__teacher__course_location'),
        class_level=F('name_of_exam__class_level')
    )

    # Apply filters
    filter_params = Q()
    if 'course_location' in request.GET:
        filter_params &= Q(name_of_exam__class_information__teacher__course_location=request.GET['course_location'])
    if 'teacher' in request.GET:
        filter_params &= Q(name_of_exam__class_information__teacher__id=request.GET['teacher'])
    if 'class_time' in request.GET:
        filter_params &= Q(student__Time=request.GET['class_time'])
    if 'added_by' in request.GET:
        filter_params &= Q(user__id=request.GET['added_by'])

    student_exams = student_exams.filter(filter_params)

    # Get unique values for filter fields
    unique_locations = student_exams.values_list('teacher_location', flat=True).distinct()
    unique_teachers = student_exams.values('teacher_id', 'teacher_first_name', 'teacher_last_name').distinct()
    unique_class_times = Candidate.objects.filter(
        course_intake__in=student_exams.values_list('course_intake', flat=True)
    ).values_list('Time', flat=True).distinct()
    unique_added_by = student_exams.values('user__id', 'user__first_name', 'user__last_name').distinct()

    levels = ['A1.1', 'A1.2', 'A2.1', 'A2.2', 'B1.1', 'B1.2', 'B2.1', 'B2.2']

    # Count unique students for each group
    student_counts = student_exams.values(
        'course_intake', 'class_no', 'added_by_id', 'name_of_exam'
    ).annotate(
        total_students=Count('student', distinct=True)
    )

    # Prepare grouped data for template
    grouped_data = {}
    for exam in student_exams:
        key = (exam.course_intake, exam.class_no, exam.added_by_id)

        if key not in grouped_data:
            class_time = Candidate.objects.filter(
                course_intake=exam.course_intake
            ).values('Time').annotate(
                count=Count('Time')
            ).order_by('-count').first()

            student_count = next(
                (item['total_students'] for item in student_counts
                 if item['course_intake'] == exam.course_intake
                 and item['class_no'] == exam.class_no
                 and item['added_by_id'] == exam.added_by_id
                 and item['name_of_exam'] == exam.name_of_exam.id),
                0
            )

            grouped_data[key] = {
                'course_intake': exam.course_intake,
                'class_no': exam.class_no,
                'teacher': f"{exam.teacher_first_name} {exam.teacher_last_name}",
                'teacher_id': exam.teacher_id,
                'location': exam.teacher_location,
                'class_time': class_time['Time'] if class_time else "N/A",
                'examinations': [],
                'current_level': "N/A",
                'previous_exam': "N/A",
                'next_exam': "N/A",
                'added_by': exam.added_by_name,
                'added_by_id': exam.added_by_id,
                'total_students': student_count,
            }

        grouped_data[key]['examinations'].append({
            'name': exam.name_of_exam.examination_name,
            'level': exam.class_level,
        })

        if exam.class_level in levels:
            current_index = levels.index(exam.class_level)
            grouped_data[key]['current_level'] = exam.class_level
            grouped_data[key]['previous_exam'] = next((level for level in reversed(levels[:current_index])), "N/A")
            grouped_data[key]['next_exam'] = next((level for level in levels[current_index + 1:]), "N/A")

    active_filters = {k: v for k, v in request.GET.items() if
                      k in ['course_location', 'teacher', 'class_time', 'added_by'] and v}

    context = {
        'grouped_data': list(grouped_data.values()),
        'unique_locations': sorted(unique_locations),
        'unique_teachers': unique_teachers,
        'unique_class_times': sorted(unique_class_times),
        'unique_added_by': unique_added_by,
        'active_filters': active_filters,
    }
    return render(request, 'assessments.html', context)


from django.db import connection
from collections import defaultdict


def present_examinations(request):
    course_class_no = request.GET.get('course_class_no')
    course_intake = request.GET.get('course_intake')
    teacher_id = request.GET.get('teacher_id')
    added_by = request.GET.get('added_by')

    debug_info = {
        'params': {
            'course_class_no': course_class_no,
            'course_intake': course_intake,
            'teacher_id': teacher_id,
            'added_by': added_by
        }
    }

    student_exams = StudentExam.objects.select_related(
        'name_of_exam__class_information__teacher',
        'name_of_exam__class_information__course_intake',
        'user'
    )

    if course_class_no:
        student_exams = student_exams.filter(name_of_exam__class_information__course_class_no=course_class_no)
    if course_intake:
        student_exams = student_exams.filter(
            name_of_exam__class_information__course_intake__course_intake=course_intake)
    if teacher_id:
        student_exams = student_exams.filter(name_of_exam__class_information__teacher__id=teacher_id)
    if added_by:
        student_exams = student_exams.filter(user__id=added_by)

    exams_dict = defaultdict(lambda: {
        'student_exams': [],
        'total_students': 0,
        'passed_students': 0,
        'participated_students': 0,  # Added: Count of students who participated in the exam
        'added_by': set(),  # Use a set to store unique users who added exams
    })

    for student_exam in student_exams:
        exam = student_exam.name_of_exam
        exam_key = exam.id

        if exam_key not in exams_dict:
            exams_dict[exam_key].update({
                'id': exam.id,
                'examination_name': exam.examination_name or exam.class_level,
                'class_information': {
                    'course_class_no': exam.class_information.course_class_no
                },
                'teacher': f"{exam.class_information.teacher.first_name} {exam.class_information.teacher.last_name}",
                'date_scheduled': "TBS",
                'date_entered': exam.date_added.strftime("%A, %B %d, %Y"),
            })

        exams_dict[exam_key]['student_exams'].append(student_exam)
        exams_dict[exam_key]['total_students'] += 1

        # Updated: Count participated students and passed students
        if student_exam.percentage_score:
            exams_dict[exam_key]['participated_students'] += 1
            if float(student_exam.percentage_score.rstrip('%')) >= 60:
                exams_dict[exam_key]['passed_students'] += 1

        # Add the user who added this exam to the set
        exams_dict[exam_key]['added_by'].add(f"{student_exam.user.first_name} {student_exam.user.last_name}")

    exams_data = []
    for exam_data in exams_dict.values():
        participated_students = exam_data['participated_students']  # Updated: Use participated_students
        passed_students = exam_data['passed_students']

        # Updated: Calculate pass rate based on participated students
        if participated_students > 0:
            pass_rate = (passed_students / participated_students) * 100
            exam_data['pass_rate'] = f"{passed_students}/{participated_students}"
            exam_data['pass_rate_class'] = (
                "pass-rate-high" if pass_rate >= 80 else
                "pass-rate-medium" if pass_rate >= 60 else
                "pass-rate-low"
            )
        else:
            exam_data['pass_rate'] = "0/0"
            exam_data['pass_rate_class'] = "pass-rate-none"

        # Updated: Calculate participation rate
        total_class_students = Candidate.objects.filter(course_intake=course_intake).count()

        if total_class_students > 0:
            participation_rate = (participated_students / total_class_students) * 100
            exam_data['participation_rate'] = f"{participated_students}/{total_class_students}"
            exam_data['participation_class'] = (
                "participation-high" if participation_rate >= 90 else
                "participation-medium" if participation_rate >= 75 else
                "participation-low"
            )
        else:
            exam_data['participation_rate'] = "0/0"
            exam_data['participation_class'] = "participation-none"

        # Convert the set of users who added exams to a comma-separated string
        exam_data['added_by'] = ", ".join(sorted(exam_data['added_by']))

        exams_data.append(exam_data)

    debug_info['query'] = str(student_exams.query)
    debug_info['sql'] = connection.queries[-1]['sql'] if connection.queries else "No SQL query logged"
    debug_info['exam_count'] = len(exams_data)

    context = {
        'exams_data': exams_data,
        'debug_info': debug_info,
    }
    return render(request, 'report_exams.html', context)


def view_student_exams(request, exam_id):
    examination = get_object_or_404(Examination.objects.select_related('class_information'), id=exam_id)
    exam_name = examination.examination_name or examination.class_level
    course_class_no = request.GET.get('course_class_no') or request.POST.get('course_class_no')

    cohorts = Cohort.objects.filter(course_class_no=course_class_no)

    if cohorts.exists():
        cohort = cohorts.first()
        students = Candidate.objects.filter(course_intake=cohort.course_intake)
        exams = StudentExam.objects.filter(
            name_of_exam_id=examination.id,
            student__course_intake=cohort.course_intake
        ).select_related('student', 'user').prefetch_related(
            Prefetch('examination_report', queryset=ExaminationReport.objects.all(), to_attr='report')
        ).annotate(
            speaking_display=F('speaking_score'),
            listening_display=F('listening_score'),
            reading_display=F('reading_score'),
            writing_display=F('writing_score')
        )

        # Get unique users who added the exams
        exam_adders = set(exam.user for exam in exams if exam.user)

        # Get the corresponding teachers
        teachers = Teacher.objects.filter(user__in=exam_adders)

        added_by = ", ".join(
            [f"{teacher.first_name} {teacher.last_name}" for teacher in teachers]) or "Unknown Teacher(s)"
    else:
        cohort = None
        students = []
        exams = []
        added_by = "Unknown Teacher(s)"
        if course_class_no:
            messages.error(request, f"No cohort found with class number: {course_class_no}")

    context = {
        'examination': examination,
        'exam_name': exam_name,
        'students': students,
        'cohort': cohort,
        'exams': exams,
        'way_forward_choices': ExaminationReport.WAY_FORWARD_CHOICES,
        'added_by': added_by,
    }

    return render(request, 'viewing_exams.html', context)


def admin_approve_report(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(ExaminationReport, id=report_id)
        decision = request.POST.get('admin_decision')
        notes = request.POST.get('admin_notes')

        if decision in ['approve', 'reject']:
            report.admin_decision = 'approved' if decision == 'approve' else 'rejected'
            report.admin_notes = notes
            report.admin_decision_date = timezone.now()
            report.save()

        return redirect('view_student_exams', exam_id=report.student_exam.name_of_exam.id)

    # If not a POST request, redirect to the same view_student_exams URL
    report = get_object_or_404(ExaminationReport, id=report_id)
    return redirect('view_student_exams', exam_id=report.student_exam.name_of_exam.id)


@login_required(login_url='login')
def student_exam_result(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate

    exams = StudentExam.objects.filter(student=candidate)

    context = {
        'candidate': candidate,
        'exams': exams,
        'skills': ['speaking', 'listening', 'reading', 'writing'],
    }

    return render(request, 'students_viewing_exams.html', context)


@login_required
def exam_list(request):
    exams = Examination.objects.filter(user=request.user)
    return render(request, 'exams_list.html', {'exams': exams})


@login_required
def edit_exams(request, exam_id):
    examination = get_object_or_404(Examination, id=exam_id, user=request.user)
    student_exams = StudentExam.objects.filter(name_of_exam=examination)
    missed_assessment_reasons_choices = StudentExam._meta.get_field('missed_exam_reason').choices

    if request.method == 'POST':
        for student_exam in student_exams:
            score_key = f'score_{student_exam.id}'
            reason_key = f'reason_{student_exam.id}'

            percentage_score = request.POST.get(score_key, '').strip()
            missed_exam_reason = request.POST.get(reason_key, '').strip()

            # Update the student_exam record
            if percentage_score:
                student_exam.percentage_score = percentage_score
            if missed_exam_reason:
                student_exam.missed_exam_reason = missed_exam_reason

            student_exam.save()

        messages.success(request, "Exam records updated successfully!")
        return redirect('exam_list')  # Assuming 'exam_list' is the name of your exam listing view

    context = {
        'examination': examination,
        'student_exams': student_exams,
        'missed_assessment_reasons_choices': missed_assessment_reasons_choices,
    }
    return render(request, 'edit_exams.html', context)


@login_required
def delete_student_exam(request, student_exam_id):
    student_exam = get_object_or_404(StudentExam, id=student_exam_id)
    exam_id = student_exam.name_of_exam.id
    course_class_no = request.GET.get('course_class_no') or request.POST.get('course_class_no')

    student_exam.delete()

    # Preparing the redirection URL
    redirect_url = reverse('manage_student_exams', kwargs={'exam_id': exam_id})
    if course_class_no:
        redirect_url += f'?course_class_no={course_class_no}'

    return HttpResponseRedirect(redirect_url)


@login_required(login_url='/teacher-login/')
def manage_student_exams(request, exam_id):
    examination = get_object_or_404(Examination, id=exam_id)
    course_class_no = request.GET.get('course_class_no') or request.POST.get('course_class_no')
    cohorts = Cohort.objects.filter(course_class_no=course_class_no)
    time_filter = request.GET.get('time_filter') or request.POST.get('time_filter')

    # Only redirect if it's a GET request and there's no time filter
    if request.method == "GET" and not time_filter:
        return redirect(reverse('filter_students_for_exam', kwargs={'exam_id': exam_id}) +
                        f'?course_class_no={course_class_no}')

    # Retrieve the current logged-in teacher's course location.
    teacher_course_location = None
    if request.user.is_authenticated and hasattr(request.user, 'teacher'):
        teacher_course_location = request.user.teacher.course_location

    if cohorts.exists():
        cohort = cohorts.first()
        students = Candidate.objects.filter(course_intake=cohort.course_intake)
        if time_filter:
            students = students.filter(
                Time=time_filter,
                Course_Location=teacher_course_location
            )

        # Annotate students with their exam data
        students = students.annotate(
            student_exam_id=Subquery(
                StudentExam.objects.filter(
                    name_of_exam=examination,
                    student=OuterRef('pk')
                ).values('id')[:1]
            )
        )
    else:
        cohort = None
        students = []
        if course_class_no:
            messages.error(request, f"No cohort found with class number: {course_class_no}")

    missed_assessment_reasons = StudentExam._meta.get_field('missed_exam_reason').choices

    if request.method == "POST":
        # NEW: Handle autosave AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            student_id = request.POST.get('student_id')
            skill = request.POST.get('skill')
            score = request.POST.get('score')
            total = request.POST.get('total')
            missed_reason = request.POST.get('missed_reason')

            student = get_object_or_404(Candidate, id=student_id)
            student_exam, created = StudentExam.objects.get_or_create(
                name_of_exam=examination,
                student=student,
                defaults={'user': request.user}
            )

            # Update the specific skill fields
            setattr(student_exam, f'{skill}_score', Decimal(score) if score else None)
            setattr(student_exam, f'{skill}_total', Decimal(total) if total else None)
            setattr(student_exam, f'{skill}_missed_reason', missed_reason if missed_reason else None)

            student_exam.save()

            # Recalculate percentage score
            student_exam.calculate_and_save_percentage_score()

            # Determine failed assessments
            failed_assessments = [s for s in ['speaking', 'listening', 'reading', 'writing']
                                  if getattr(student_exam, f'{s}_score') and
                                  getattr(student_exam, f'{s}_total') and
                                  float(getattr(student_exam, f'{s}_score')) < 0.6 * float(
                    getattr(student_exam, f'{s}_total'))]

            return JsonResponse({
                'success': True,
                'percentage_score': student_exam.percentage_score,
                'failed_assessments': failed_assessments
            })

        # Existing POST handling code
        save_all = request.POST.get('save_all') == 'true'
        student_ids = [request.POST.get(f'student_id_{i}') for i in range(len(students))] if save_all else [
            request.GET.get('student_id')]

        # Store global totals from the POST request
        global_totals = {skill: request.POST.get(f'{skill}_total', '') for skill in
                         ['speaking', 'listening', 'reading', 'writing']}
        request.session['global_totals'] = global_totals

        any_changes = False
        for student_id in student_ids:
            if student_id:
                student = get_object_or_404(Candidate, id=student_id)
                student_exam, created = StudentExam.objects.get_or_create(
                    name_of_exam=examination,
                    student=student,
                    defaults={'user': request.user}
                )

                changes = {}
                errors = []
                skill_percentages = []

                for skill in ['speaking', 'listening', 'reading', 'writing']:
                    score = request.POST.get(f'{skill}_score_{student_id}', '').strip()
                    total = request.POST.get(f'{skill}_total_{student_id}', '').strip() or global_totals.get(skill, '')
                    reason = request.POST.get(f'{skill}_missed_reason_{student_id}', '').strip()

                    logger.debug(
                        f"Processing {skill} for student {student_id}: score={score}, total={total}, reason={reason}")

                    if score or total:
                        try:
                            score_decimal = Decimal(score) if score else Decimal('0')
                            total_decimal = Decimal(total) if total else None

                            if total_decimal is None or total_decimal <= 0:
                                errors.append(f"{skill.capitalize()} total must be greater than 0.")
                            elif score_decimal > total_decimal:
                                errors.append(f"{skill.capitalize()} score cannot be greater than the total.")
                            else:
                                percentage = (score_decimal / total_decimal) * 100
                                changes[f'{skill}_score'] = score_decimal
                                changes[f'{skill}_total'] = total_decimal
                                changes[f'{skill}_missed_reason'] = ''

                        except InvalidOperation:
                            errors.append(f"Invalid {skill} score or total entered. Please enter valid numbers.")
                    elif reason:
                        changes[f'{skill}_missed_reason'] = reason
                        changes[f'{skill}_score'] = None
                        changes[f'{skill}_total'] = None
                    else:
                        # If all fields are empty, don't change anything
                        pass

                # Calculate overall percentage score
                if skill_percentages:
                    overall_score = sum(skill_percentages) / len(skill_percentages)
                    changes['percentage_score'] = Decimal(overall_score).quantize(Decimal('0.01'))
                    changes['missed_exam_reason'] = ''
                elif 'missed_exam_reason' in request.POST:
                    overall_reason = request.POST.get('missed_exam_reason', '').strip()
                    if overall_reason:
                        changes['percentage_score'] = None
                        changes['missed_exam_reason'] = overall_reason
                    else:
                        # If no valid scores and no overall reason, don't change overall fields
                        pass

                logger.debug(f"Changes for student {student_id}: {changes}")
                logger.debug(f"Errors for student {student_id}: {errors}")

                # Update and save the student exam instance
                if changes:
                    for field, value in changes.items():
                        setattr(student_exam, field, value)
                    try:
                        student_exam.save()
                        any_changes = True
                        logger.debug(
                            f"Successfully updated exam for student {student.id}. New average: {student_exam.percentage_score}")

                        if not save_all:
                            messages.success(request,
                                             f"Examination record for student {student.First_Name} {student.Last_Name} updated successfully.")
                    except Exception as e:
                        logger.exception(f"Error saving data for student {student_id}")
                        errors.append(f"Error saving data: {str(e)}")

                if errors:
                    for error in errors:
                        messages.error(request, f"Error for {student.First_Name} {student.Last_Name}: {error}")
                elif not changes and not save_all:
                    messages.info(request,
                                  f"No changes were made for student {student.First_Name} {student.Last_Name}.")

        if save_all:
            if any_changes:
                messages.success(request, "All examination records updated successfully.")
            else:
                messages.info(request, "No changes were made to any examination records.")

        # Redirect to manage student exams page
        redirect_url = reverse('manage_student_exams', kwargs={'exam_id': exam_id})
        if course_class_no:
            redirect_url += f'?course_class_no={course_class_no}'
        return redirect(redirect_url)

    # For GET requests, retrieve global totals from session or initialize empty
    global_totals = request.session.get('global_totals', {})
    if not global_totals:
        global_totals = {skill: '' for skill in ['speaking', 'listening', 'reading', 'writing']}
        request.session['global_totals'] = global_totals

    # Modify this part to create a dictionary of examination reports
    student_exams = StudentExam.objects.filter(
        id__in=[student.student_exam_id for student in students if student.student_exam_id]
    ).select_related('student')
    examination_reports = ExaminationReport.objects.filter(
        student_exam__in=student_exams
    ).select_related('student_exam')

    # Create a dictionary of examination reports keyed by student_exam_id
    examination_reports_dict = {report.student_exam_id: report for report in examination_reports}

    # Create a dictionary of student exams keyed by student_id
    student_exams_dict = {exam.student_id: exam for exam in student_exams}

    # Create a dictionary to store whether each student has passed
    students_passed_dict = {}

    for student_exam in student_exams:
        all_scores_above_60 = all(
            float(getattr(student_exam, f'{skill}_score', 0) or 0) >=
            0.6 * float(getattr(student_exam, f'{skill}_total', 1) or 1)
            for skill in ['speaking', 'listening', 'reading', 'writing']
        )
        students_passed_dict[student_exam.student_id] = all_scores_above_60

    # Create admin_decisions_dict (if not already created)
    admin_decisions_dict = {report.student_exam.student_id: report.admin_decision
                            for report in examination_reports}

    class_report, created = ClassReport.objects.get_or_create(
        examination=examination,
        cohort=cohort
    )
    context = {
        'examination': examination,
        'students': students,
        'cohort': cohort,
        'missed_assessment_reasons': missed_assessment_reasons,
        'skills': ['speaking', 'listening', 'reading', 'writing'],
        'time_choices': dict(Candidate._meta.get_field('Time').choices),
        'current_time_filter': time_filter,
        'global_totals': global_totals,
        # ... Reports ...
        'examination_reports_dict': examination_reports_dict,
        'student_exams_dict': student_exams_dict,
        'way_forward_choices': ExaminationReport.WAY_FORWARD_CHOICES,
        'admin_decisions_dict': admin_decisions_dict,
        'students_passed_dict': students_passed_dict,  # Add this line
        'class_report': class_report,

    }

    return render(request, 'posting_exams.html', context)


@login_required
@require_POST
def save_overall_class_report(request):
    examination_id = request.POST.get('examination_id')
    cohort_id = request.POST.get('cohort_id')
    overall_report = request.POST.get('overall_report')

    print(
        f"Received data: examination_id={examination_id}, cohort_id={cohort_id}, overall_report={overall_report}")  # Debug print

    if not all([examination_id, cohort_id, overall_report]):
        print("Missing required fields")  # Debug print
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

    try:
        examination = Examination.objects.get(id=examination_id)
        cohort = Cohort.objects.get(id=cohort_id)

        class_report, created = ClassReport.objects.update_or_create(
            examination=examination,
            cohort=cohort,
            defaults={'overall_report': overall_report}
        )

        print(f"ClassReport {'created' if created else 'updated'}: id={class_report.id}")  # Debug print

        return JsonResponse({'status': 'success', 'message': 'Overall class report saved successfully'})
    except (Examination.DoesNotExist, Cohort.DoesNotExist) as e:
        print(f"Error: {str(e)}")  # Debug print
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug print
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)


@login_required
@require_POST
def autosave_exam_field(request, exam_id):
    examination = get_object_or_404(Examination, id=exam_id)
    student_id = request.POST.get('student_id')
    skill = request.POST.get('skill')
    field_type = request.POST.get('field_type')
    value = request.POST.get('value')

    try:
        student_exam, created = StudentExam.objects.get_or_create(
            name_of_exam=examination,
            student_id=student_id,
            defaults={'user': request.user}
        )

        if field_type == 'score':
            setattr(student_exam, f'{skill}_score', value)
        elif field_type == 'total':
            setattr(student_exam, f'{skill}_total', value)
        elif field_type == 'missed_reason':
            setattr(student_exam, f'{skill}_missed_reason', value)

        student_exam.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Filter students exam
@login_required(login_url='/teacher-login/')
def filter_students_for_exam(request):
    course_class_no = request.GET.get('course_class_no')
    time_choices = dict(Candidate._meta.get_field('Time').choices)
    time_choices = {k: v for k, v in time_choices.items() if k is not None}

    # Fetch the Cohort information
    cohort = Cohort.objects.filter(course_class_no=course_class_no).first()

    context = {
        'time_choices': time_choices,
        'course_class_no': course_class_no,
        'cohort': cohort,
    }

    if request.method == 'POST':
        selected_time = request.POST.get('time_filter')
        if selected_time:
            return redirect(
                reverse('existing_exams') + f'?course_class_no={course_class_no}&time_filter={selected_time}')

    return render(request, 'filter_students_for_exam.html', context)


@login_required(login_url='/teacher-login/')
def create_examination(request):
    if request.method == 'POST':
        form = ExaminationForm(request.POST)
        if form.is_valid():
            examination = form.save(commit=False)
            examination.user = request.user
            examination.save()
            return redirect('class_numbers')
    else:
        form = ExaminationForm(user=request.user)

    return render(request, 'creating_exams.html', {'form': form})


@login_required(login_url='/teacher-login/')
def existing_exams(request):
    time_filter = request.GET.get('time_filter')
    course_class_no = request.GET.get('course_class_no')

    exams = Examination.objects.all()
    if course_class_no:
        exams = exams.filter(class_information__course_class_no=course_class_no)

    exam_data = []
    for exam in exams.select_related('class_information__teacher', 'class_information__course_intake'):
        scheduled_exam = ScheduledExam.objects.filter(user=request.user, examination=exam).first()

        # Count total students in the class
        total_students = Candidate.objects.filter(
            course_intake=exam.class_information.course_intake.course_intake
        ).count()

        # Count students with grades for this exam
        students_with_grades = StudentExam.objects.filter(
            name_of_exam=exam
        ).exclude(
            Q(percentage_score__isnull=True) | Q(percentage_score='')
        ).count()

        # Calculate average score for this exam
        student_exams = StudentExam.objects.filter(
            name_of_exam=exam
        ).exclude(
            Q(percentage_score__isnull=True) | Q(percentage_score='')
        )

        scores = []
        for student_exam in student_exams:
            try:
                score = Decimal(student_exam.percentage_score.rstrip('%'))
                scores.append(score)
            except (InvalidOperation, AttributeError):
                pass

        average_score = sum(scores) / len(scores) if scores else None

        if average_score is not None:
            average_score = round(average_score, 2)

        exam_data.append({
            'exam': exam,
            'scheduled_date': scheduled_exam.scheduled_date if scheduled_exam else None,
            'total_students': total_students,
            'students_with_grades': students_with_grades,
            'average_score': average_score,
        })

    context = {
        'exam_data': exam_data,
        'time_filter': time_filter,
        'course_class_no': course_class_no,
    }

    return render(request, 'existing_exams.html', context)


@login_required
@require_POST
def update_scheduled_date(request):
    exam_id = request.POST.get('exam_id')
    scheduled_date = request.POST.get('scheduled_date')

    if not exam_id or not scheduled_date:
        return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

    try:
        examination = Examination.objects.get(id=exam_id)
        scheduled_exam, created = ScheduledExam.objects.get_or_create(
            user=request.user,
            examination=examination,
            defaults={'scheduled_date': timezone.now()}  # Provide a default value
        )

        # Parse the datetime and make it timezone-aware
        parsed_date = parse_datetime(scheduled_date)
        if parsed_date is not None:
            aware_datetime = timezone.make_aware(parsed_date, timezone.get_current_timezone())
            scheduled_exam.scheduled_date = aware_datetime
            scheduled_exam.save()
            return JsonResponse({'status': 'success', 'message': 'Date updated successfully'})
        else:
            logger.warning(f"Invalid date format received: {scheduled_date}")
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)
    except Examination.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Examination not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in update_scheduled_date: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)


@login_required(login_url='/teacher-login/')
def class_numbers(request):
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        cohorts = Cohort.objects.filter(teacher=teacher).order_by('course_class_no').select_related('course_intake')
        unique_class_numbers = [(cohort.course_class_no, str(cohort.course_intake)) for cohort in cohorts]
    else:
        unique_class_numbers = []

    context = {
        'unique_class_numbers': unique_class_numbers,
    }
    return render(request, 'filter_with_class.html', context)
