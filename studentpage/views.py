from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from .models import Transcript
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CandidateSerializer

# Wifi, install getmac with pip install getmac
from getmac import get_mac_address

# Password Reset Process
from django.core.mail import send_mail
from .models import PasswordResetCode
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

User = get_user_model()


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email__iexact=email).first()
        if user:
            candidate = getattr(user, 'candidate', None)
            if candidate:
                if PasswordResetCode.can_send_email(user):
                    code = PasswordResetCode.generate_code()
                    PasswordResetCode.objects.create(user=user, code=code)

                    # Prepare the email
                    context = {
                        'code': code,
                        'user': user,
                    }
                    html_message = render_to_string('password_reset_email.html', context)
                    plain_message = strip_tags(html_message)

                    # Send email with the code
                    try:
                        send_mail(
                            'Password Reset Code - AG German Institute',
                            plain_message,
                            None,  # Use DEFAULT_FROM_EMAIL from settings
                            [email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        messages.success(request, 'A password reset code has been sent to your email.')
                        return redirect('password_reset_verify')
                    except Exception as e:
                        messages.error(request, f'An error occurred while sending the email: {str(e)}')
                else:
                    messages.error(request, 'Too many reset attempts. Please try again later.')
            else:
                messages.error(request, 'No student profile found for this email address.')
        else:
            messages.error(request, 'No user found with that email address.')
    return render(request, 'password_reset_request.html')


def password_reset_verify(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.filter(email__iexact=email).first()
        if user:
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                code=code,
                created_at__gte=timezone.now() - timedelta(minutes=15)
            ).first()

            if reset_code:
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    candidate = getattr(user, 'candidate', None)
                    if candidate:
                        candidate.needs_password_change = False
                        candidate.save()
                    reset_code.delete()
                    messages.success(request, 'Your password has been reset successfully.')
                    return redirect('login')
                else:
                    messages.error(request, 'Passwords do not match. Please try again.')
            else:
                messages.error(request, 'Invalid or expired code. Please request a new code.')
        else:
            messages.error(request, 'No user found with that email address.')
    return render(request, 'password_reset_verify.html')


@login_required
def register_device(request):
    candidate = request.user.candidate
    if request.method == 'POST':
        mac_address = get_mac_address(ip=request.META['REMOTE_ADDR'])
        candidate.device_mac_address = mac_address
        candidate.save()
        messages.success(request, 'Device registered successfully.')
        return redirect('/')
    return render(request, 'register_device.html')


def get_client_mac(request):
    # In a real-world scenario, you'd get this from UniFi or the network
    return request.GET.get('client_mac')


def wifi_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email__iexact=email).first()

        if user:
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                candidate = Candidate.objects.filter(user=user).first()
                if candidate:
                    client_mac = get_client_mac(request)
                    if candidate.device_mac_address and candidate.device_mac_address != client_mac:
                        # Offer option to update device
                        return render(request, 'device_mismatch.html', {'client_mac': client_mac})
                    else:
                        login(request, user)
                        if not candidate.device_mac_address:
                            candidate.device_mac_address = client_mac
                            candidate.save()
                        # Here you would authorize the device with UniFi
                        return redirect('home')
                else:
                    messages.error(request, 'No candidate profile associated with this account.')
            else:
                messages.error(request, 'Email or password is not correct')
        else:
            messages.error(request, 'Account does not exist.')

    return render(request, 'wifi_login.html')


@login_required
def update_device(request):
    candidate = request.user.candidate
    if request.method == 'POST':
        client_mac = get_client_mac(request)
        if client_mac:
            candidate.device_mac_address = client_mac
            candidate.save()
            messages.success(request, 'Your device has been updated successfully.')
            # Here you would authorize the new device with UniFi
            return redirect('home')
        else:
            messages.error(request, 'Unable to detect device MAC address.')

    context = {
        'candidate': candidate,
        'current_mac': candidate.device_mac_address,
    }
    return render(request, 'update_device.html', context)


@login_required
def remove_device(request):
    candidate = request.user.candidate
    if request.method == 'POST':
        candidate.device_mac_address = None
        candidate.save()
        messages.success(request, 'Your device has been removed successfully.')
        # Here you would deauthorize the device with UniFi
    return redirect('home')


class CandidateCreateAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/login/')
def download_view(request):
    candidate = None
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate

    return render(request, 'downloads.html', {
        'candidate': candidate
    })


@login_required(login_url='/login/')
def home(request):
    candidate = None
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate
    context = {'candidate': candidate}
    return render(request, 'home.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            # Convert the email to lowercase before the query
            # and use case-insensitive filtering for the email.
            user = User.objects.filter(email__iexact=email).first()
            if user:
                # Use the user's username to authenticate, as it's case-sensitive by default.
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    # Your existing post-login logic
                    candidate = getattr(user, 'candidate', None)
                    if candidate and candidate.needs_password_change:
                        return redirect('change_password_url')
                    return redirect('/')
                else:
                    messages.error(request, 'Email or password is not correct')
            else:
                messages.error(request, 'Account does not exist.')
        return render(request, 'login.html')


from django.contrib.auth import update_session_auth_hash


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.candidate.needs_password_change = False
            user.candidate.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def coursework(request):
    candidate = None
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate
    context = {'candidate': candidate}
    return render(request, 'coursework.html', context)


@login_required(login_url='/login/')
def attendance(request):
    candidate = None
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate
    context = {'candidate': candidate}
    return render(request, 'Attendance.html', context)


@login_required(login_url='/login/')
def payments(request):
    candidate = None
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate
    context = {'candidate': candidate}
    return render(request, 'payments.html', context)


def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()  # This saves the User instance and returns it
            messages.success(request, f'Account was created for {user.username}')
            return redirect('login')
    context = {'form': form}
    return render(request, 'register.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import DocumentUploadForm


@login_required(login_url='/login/')
def upload_documents(request):
    candidate, _ = Candidate.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            saved_instance = form.save()  # Correctly save the instance here

            transcripts_files = request.FILES.getlist('other_transcripts')
            for file in transcripts_files:
                Transcript.objects.create(candidate=saved_instance, other_transcripts=file)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response_data = {
                    field_name: getattr(saved_instance, field_name).url
                    for field_name in form.cleaned_data
                    if getattr(saved_instance, field_name, None)
                }
                return JsonResponse(response_data)

            messages.success(request, 'Your documents have been updated successfully.')
            return redirect('upload_documents')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': form.errors.as_json()}, status=400)
    else:
        form = DocumentUploadForm(instance=candidate)

    # Organize fields into categories
    personal_documents = ['Birth_certificate', 'identification_card_file', 'photo', 'passport']
    educational_documents = ['High_School_file', 'University_file']
    professional_documents = ['Nursing_Certificate', 'Licence_file', 'Institution_file', 'resume_file']

    # Filter form fields based on the category
    form_fields = {field.name: field for field in form}
    categories = {
        'personal_documents': {key: form_fields[key] for key in personal_documents},
        'educational_documents': {key: form_fields[key] for key in educational_documents},
        'professional_documents': {key: form_fields[key] for key in professional_documents},
    }

    context = {
        'form': form,
        'candidate': candidate,
        'transcripts': candidate.transcripts.all(),
        'categories': categories,  # Add the categories to the context
    }
    return render(request, 'upload_documents.html', context)


@login_required(login_url='/login/')
def delete_transcript(request, transcript_id):
    transcript = get_object_or_404(Transcript, id=transcript_id, candidate__user=request.user)
    transcript.delete()
    messages.success(request, "Transcript deleted successfully.")
    return redirect('upload_documents')  # Replace 'upload_documents' with the name of your view that displays the form


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Candidate


@csrf_exempt
def delete_document(request):
    if request.method == "POST":
        doc_field = request.POST.get("doc_field")
        candidate_id = request.POST.get("candidate_id")

        candidate = get_object_or_404(Candidate, pk=candidate_id)
        if hasattr(candidate, doc_field):
            file_field = getattr(candidate, doc_field)
            if file_field:
                file_field.delete()  # Delete the file
                candidate.save()  # Save the candidate to update the database entry
                return JsonResponse({"success": True, "message": "Document deleted successfully."}, status=200)
            else:
                return JsonResponse({"success": False, "message": "Document not found."}, status=404)
        else:
            return JsonResponse({"success": False, "message": "Invalid document field."}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


def get_document_field(doc_type):
    """
    Returns the model field name for a given document type.
    """
    # Mapping of document types to Candidate model fields
    doc_type_mapping = {
        'personal_documents': 'personal_document_field',  # Replace 'personal_document_field' with actual field names
        'educational_documents': 'educational_document_field',
        'professional_documents': 'professional_document_field',
        'transcripts': 'other_transcripts',
    }
    return doc_type_mapping.get(doc_type)


from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.management import call_command
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def import_candidates_view(request):
    if request.method == "POST":
        call_command('import_candidates')
        # Redirect to a new URL or return a success message
        return HttpResponseRedirect(reverse('your-success-view'))
    else:
        return HttpResponseRedirect(reverse('your-fallback-view'))


# Resume builder
from django.views.decorators.http import require_http_methods
from .models import Resume

# Pdf
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse


@login_required
@require_http_methods(["GET", "POST"])
def resume_builder(request):
    candidate = Candidate.objects.get(user=request.user)
    resume, created = Resume.objects.get_or_create(candidate=candidate)

    if request.method == 'POST':
        # Update Candidate model fields
        candidate.First_Name = request.POST.get('firstname', candidate.First_Name)
        candidate.Last_Name = request.POST.get('lastname', candidate.Last_Name)
        candidate.email_address = request.POST.get('email', candidate.email_address)
        candidate.phone_number = request.POST.get('phone', candidate.phone_number)
        candidate.Street_Address = request.POST.get('address', candidate.Street_Address)
        if 'profile_photo' in request.FILES:
            candidate.photo = request.FILES['profile_photo']
        candidate.save()

        # Update Resume model fields
        resume.summary = request.POST.get('summary', '')
        resume.company = request.POST.getlist('company[]')
        resume.role = request.POST.getlist('role[]')
        resume.work_tenure = request.POST.getlist('work_tenure[]')
        resume.responsibilities = request.POST.getlist('responsibilities[]')
        resume.school = request.POST.getlist('school[]')
        resume.qualification = request.POST.getlist('qualification[]')
        resume.education_tenure = request.POST.getlist('education_tenure[]')
        resume.skills = request.POST.getlist('skills[]')
        resume.languages = request.POST.getlist('languages[]')
        resume.certifications = request.POST.getlist('certifications[]')
        resume.hobbies = request.POST.getlist('hobbies[]')
        resume.reference_names = request.POST.getlist('reference_names[]')
        resume.reference_companies = request.POST.getlist('reference_companies[]')
        resume.reference_contacts = request.POST.getlist('reference_contacts[]')
        resume.save()

        return redirect('resume_preview')

    context = {
        'candidate': candidate,
        'resume': resume
    }
    return render(request, 'resume_builder.html', context)


@login_required
def resume_preview(request):
    candidate = get_object_or_404(Candidate, user=request.user)
    resume = get_object_or_404(Resume, candidate=candidate)

    context = {
        'candidate': candidate,
        'resume': resume,
    }
    return render(request, 'resume_preview.html', context)


@login_required
def generate_pdf_resume(request):
    candidate = Candidate.objects.get(user=request.user)
    resume, created = Resume.objects.get_or_create(candidate=candidate)

    template = get_template('pdf_resume_template.html')
    context = {
        'candidate': candidate,
        'resume': resume,
    }
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response[
            'Content-Disposition'] = f'attachment; filename="{candidate.First_Name}_{candidate.Last_Name}_Resume.pdf"'
        return response
    return HttpResponse('Error Rendering PDF', status=400)


# Dean updated
from .forms import ResumeForm


@login_required(login_url='/login/')
def manage_resume(request):
    candidate = get_object_or_404(Candidate, user=request.user)
    resume = Resume.objects.filter(candidate=candidate).order_by('-version').first()

    if resume is None:
        resume = Resume(candidate=candidate, version=1, is_current=True)
        resume.save()

    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=resume)
        if form.is_valid():
            new_resume = form.save(commit=False)
            new_resume.candidate = candidate
            new_resume.version = resume.version + 1
            new_resume.is_current = True
            new_resume.pk = None  # This will create a new instance
            new_resume.save()

            # Set the old resume to not current
            resume.is_current = False
            resume.save()

            messages.success(request, 'Your resume has been updated successfully.')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('manage_resume')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'There was an error updating your resume. Please check the form and try again.')
    else:
        form = ResumeForm(instance=resume)

    context = {
        'form': form,
        'candidate': candidate,
        'resume': resume,
        'photo_url': candidate.photo.url if candidate.photo else None,
    }
    return render(request, 'manage_resume.html', context)


@login_required
def generate_resume_preview(request):
    # Fetch the resume data
    resume = Resume.objects.filter(candidate__user=request.user, is_current=True).first()

    if not resume:
        return JsonResponse({'error': 'No resume found'}, status=404)

    # Prepare the data for the preview
    preview_data = {
        'fullName': f"{resume.candidate.First_Name} {resume.candidate.Last_Name}",
        'jobTitle': resume.candidate.Qualification or "Not specified",  # Using Qualification as job title
        'summary': resume.summary,
        'contacts': f"{resume.candidate.email_address} | {resume.candidate.phone_number}",
        'experience': resume.work_experiences,
        'education': resume.educations,
        'certifications': resume.certifications,
        'skills': resume.technical_skills + resume.soft_skills if resume.technical_skills and resume.soft_skills else [],
        'languages': resume.languages,
        'interests': resume.interests or [],
        'references': resume.references,
    }

    return JsonResponse(preview_data)