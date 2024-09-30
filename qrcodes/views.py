from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.core.cache import cache
from django.utils import timezone
from .models import CandidateQRCode, QRCodeScan
from studentpage.models import Candidate
# Authentication resources
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
# Payments
from payments.models import PaymentRecord
from django.db.models import Sum
from invoices.models import SchoolFee

def qr_scanner_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            # Redirect to the 'next' parameter if it exists, otherwise to 'student_qr_codes'
            next_url = request.GET.get('next') or reverse('student_qr_codes')
            return redirect(next_url)
        else:
            return render(request, 'qr_scanner_login.html', {'error': 'Invalid credentials'})
    return render(request, 'qr_scanner_login.html')


def qr_scanner_logout(request):
    logout(request)
    return redirect('qr_scanner_login')


def get_filtered_data():
    cache_key = 'filtered_candidate_data'
    cached_data = cache.get(cache_key)
    if cached_data is None:
        candidates = Candidate.objects.select_related('qr_code').all()
        course_locations = list(dict(Candidate.COURSE_LOCATION).values())
        course_times = list(dict(Candidate.TIME).values())
        course_intakes = list(Candidate.objects.values_list('course_intake', flat=True).distinct())

        cached_data = {
            'candidates': candidates,
            'course_locations': course_locations,
            'course_times': course_times,
            'course_intakes': course_intakes,
        }
        cache.set(cache_key, cached_data, 3600)  # Cache for 1 hour
    return cached_data


@login_required(login_url='qr_scanner_login')
def student_qr_codes(request):
    filtered_data = get_filtered_data()
    candidates = filtered_data['candidates']

    paginator = Paginator(candidates, 20)  # Show 20 candidates per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'candidates': page_obj,
        'course_locations': filtered_data['course_locations'],
        'course_times': filtered_data['course_times'],
        'course_intakes': filtered_data['course_intakes'],
    }
    return render(request, 'student_qr_codes.html', context)


@login_required(login_url='qr_scanner_login')
def scan_qr_code(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    qr_code = get_object_or_404(CandidateQRCode, candidate=candidate)

    scan = QRCodeScan.objects.create(
        qr_code=qr_code,
        scanned_at=timezone.now(),
        location=request.GET.get('location', candidate.Course_Location),
        additional_info=request.GET.get('info', '')
    )

    return redirect('scan_success', scan_id=scan.id)


@login_required(login_url='qr_scanner_login')
def scan_success(request, scan_id):
    scan = get_object_or_404(QRCodeScan, id=scan_id)
    candidate = scan.qr_code.candidate

    # Fetch payment records for the candidate
    payment_records = PaymentRecord.objects.filter(candidate_name=candidate.full_name).order_by('-date_of_payment')

    # Fetch SchoolFee objects for the candidate
    fees = SchoolFee.objects.filter(candidate=candidate).order_by('starting_month')

    total_amount_paid = payment_records.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # Calculate "Payments Made" for each SchoolFee instance
    fees_with_payments = []
    remaining_amount_paid = total_amount_paid
    for fee in fees:
        if remaining_amount_paid > 0:
            payment_for_month = min(remaining_amount_paid, fee.total_amount_to_pay)
            remaining_amount_paid -= payment_for_month
        else:
            payment_for_month = 0

        fees_with_payments.append({
            'fee': fee,
            'payment_made': payment_for_month
        })

    # Calculate total fee and balance
    total_fee = sum(fee.total_amount_to_pay for fee in fees)
    balance_remaining = max(total_fee - total_amount_paid, 0)

    context = {
        'scan': scan,
        'candidate': candidate,
        'payment_records': payment_records,
        'fees_with_payments': fees_with_payments,
        'total_fee': total_fee,
        'total_amount_paid': total_amount_paid,
        'balance_remaining': balance_remaining,
    }
    return render(request, 'scan_success.html', context)

# def verify_attendance(request, scan_id):
#     scan = get_object_or_404(QRCodeScan, id=scan_id)
# Add your attendance verification logic here
# For example, you might update an Attendance model
# Attendance.objects.create(candidate=scan.qr_code.candidate, date=timezone.now().date())

# return redirect('scan_success', scan_id=scan.id)


# def report_issue(request, scan_id):
#     if request.method == 'POST':
#         scan = get_object_or_404(QRCodeScan, id=scan_id)
#         issue_description = request.POST.get('issue_description', '')
#         Add your issue reporting logic here
#         For example, you might create an Issue model and save the report
#         Issue.objects.create(scan=scan, description=issue_description)
#
#     return redirect('scan_success', scan_id=scan_id)
