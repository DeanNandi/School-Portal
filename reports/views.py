from .models import PaymentIdentification

import logging

# displaying documents
from studentpage.models import UploadedDocument, Candidate
from django.http import JsonResponse
from django.template.loader import render_to_string
from teacherpage.models import Teacher
from django.db.models import Prefetch, Q
from schooldocuments.models import Contract

# payment comparisons
from payments.models import PaymentRecord
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta

# Attendance Page
from attendancepage.models import ClassAttendance
from django.db.models import F


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


def payment_comparison(request):
    payment_records = PaymentRecord.objects.all()
    payment_identifications = PaymentIdentification.objects.all()
    filter_option = request.GET.get('filter')

    # Get date range from GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # If no dates are provided, set default to last 30 days
    if not start_date and not end_date:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
    else:
        start_date = parse_date(start_date) if start_date else None
        end_date = parse_date(end_date) if end_date else None

    # Filter records by date range
    if start_date and end_date:
        payment_records = payment_records.filter(date_of_payment__range=[start_date, end_date])

    if request.method == 'POST':
        for record in payment_records:
            transaction_details = request.POST.get(f'transaction_details_{record.id}')
            if transaction_details:
                record.transaction_details = transaction_details
                record.save()

    for record in payment_records:
        record.matched = False
        record.amount_matched = False
        for identification in payment_identifications:
            if record.transaction_details and identification.description:
                if record.transaction_details in identification.description:
                    record.matched = True
                    if str(record.amount_paid).replace(".00", "") == identification.money_in:
                        record.amount_matched = True
                    break
            if record.matched and record.amount_matched:
                break

    if filter_option == 'matched':
        payment_records = [record for record in payment_records if record.matched and record.amount_matched]
    elif filter_option == 'unmatched':
        payment_records = [record for record in payment_records if not record.matched or not record.amount_matched]

    context = {
        'payment_records': payment_records,
        'filter_option': filter_option,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'payment_comparison.html', context)


def display_teachers(request):
    teachers = Teacher.objects.all()
    context = {
        'teachers': teachers,
    }
    return render(request, 'display_teachers.html', context)


def display_documents(request):
    location = request.GET.get('location')
    search_query = request.GET.get('search')
    course_locations = Candidate.objects.values_list('Course_Location', flat=True).distinct()

    # Prefetch related Contract objects
    contract_prefetch = Prefetch('contract', queryset=Contract.objects.all())
    candidates = Candidate.objects.prefetch_related(contract_prefetch)

    if location:
        candidates = candidates.filter(Course_Location=location)

    if search_query:
        candidates = candidates.filter(
            Q(First_Name__icontains=search_query) |
            Q(Last_Name__icontains=search_query) |
            Q(admission_number__icontains=search_query)
        )

    # Filter candidates based on the existence of a contract
    candidates = [candidate for candidate in candidates if hasattr(candidate, 'contract')]

    context = {
        'candidates': candidates,
        'course_locations': course_locations,
        'search_query': search_query,
        'selected_location': location,
    }
    return render(request, 'display_documents.html', context)


def search_documents(request):
    search_query = request.GET.get('search')
    location = request.GET.get('location')

    candidates = UploadedDocument.objects.all()

    if location:
        candidates = candidates.filter(Course_Location=location)

    if search_query:
        candidates = candidates.filter(
            Q(First_Name__icontains=search_query) |
            Q(Last_Name__icontains=search_query) |
            Q(admission_number__icontains=search_query)
        )

    html = render_to_string('search_results.html', {'candidates': candidates})
    return JsonResponse({'html': html})


# Set up logging to capture errors and debug information
logger = logging.getLogger(__name__)

# Reports section
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import UserActivity, Client
from django.contrib.auth.decorators import user_passes_test


def is_client_or_user(user):
    return isinstance(user, (User, Client))


@user_passes_test(is_client_or_user, login_url='/reports_login/')
def report_view(request):
    context = {
        # Your context here
    }
    return render(request, 'reports.html', context)


def reports_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None and isinstance(user, User):
            # Existing User authentication logic
            user_activity, created = UserActivity.objects.get_or_create(user=user)

            if user_activity.is_locked_out:
                if timezone.now() < user_activity.lockout_time + timezone.timedelta(minutes=5):
                    messages.error(request, 'Account is locked. Please try again later.')
                    return render(request, 'reports_login.html')
                else:
                    user_activity.reset_failed_attempts()

            login(request, user)
            user_activity.last_login = timezone.now()
            user_activity.login_count += 1
            user_activity.reset_failed_attempts()
            user_activity.save()
            return redirect('reports')
        else:
            # Try Client authentication
            try:
                client = Client.objects.get(username=username)
                if client.check_password(password):
                    if client.is_active:
                        login(request, client, backend='path.to.your.ClientAuthBackend')
                        return redirect('reports')
                    else:
                        messages.error(request, 'This account is inactive.')
                else:
                    messages.error(request, 'Invalid username or password.')
            except Client.DoesNotExist:
                messages.error(request, 'Invalid username or password.')

    return render(request, 'reports_login.html')


def reports_logout_view(request):
    if request.user.is_authenticated:
        if isinstance(request.user, User):
            user_activity, created = UserActivity.objects.get_or_create(user=request.user)
            user_activity.last_logout = timezone.now()
            user_activity.save()
    logout(request)
    return redirect('reports_login')
