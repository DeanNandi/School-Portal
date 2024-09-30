from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Cohort
from django.db.models import Case, When, BooleanField
# Updates
from .models import Update


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.candidate.needs_password_change = False
            user.candidate.save()
            messages.success(request, 'Your password was successfully updated!')
            return redirect('homepage')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


def loginTeacher(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'teacher-login.html', context)


def logout_teacher(request):
    logout(request)
    return redirect('teacher-login')


@login_required(login_url='/login/')
def teacher_landing_page(request):
    updates = Update.objects.all()[:3]  # Retrieve the latest 3 updates
    teacher = None
    cohorts = []  # Use a list to hold multiple cohorts
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        cohorts = Cohort.objects.filter(teacher=teacher)  # Fetch cohorts for this teacher

    context = {
        'teacher': teacher,
        'cohorts': cohorts,  # Pass the list of cohorts
        'updates': updates,
    }

    return render(request, 'teacher-home.html', context)


@login_required(login_url='/login/')
def library(request):
    teacher = None
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher

    context = {
        'teacher': teacher,

    }

    return render(request, 'library.html', context)


@login_required(login_url='/login/')
def exam(request):
    teacher = None
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher

    context = {
        'teacher': teacher,

    }

    return render(request, 'examinations.html', context)


@login_required(login_url='/login/')
def classes(request):
    teacher = None
    cohorts = []  # Use a list to hold multiple cohorts
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        # Order cohorts such that pinned cohorts come first
        cohorts = Cohort.objects.filter(teacher=teacher).annotate(
            is_pinned_order=Case(
                When(is_pinned=True, then=True),
                default=False,
                output_field=BooleanField()
            )
        ).order_by('-is_pinned_order', 'id')  # Ensure a consistent order by also sorting by 'id'

    context = {
        'teacher': teacher,
        'cohorts': cohorts,
    }

    return render(request, 'classes.html', context)


def toggle_pin(request, cohort_id):
    cohort = get_object_or_404(Cohort, id=cohort_id)
    cohort.is_pinned = not cohort.is_pinned
    cohort.save()
    return redirect('classes')
