from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ExamMenschen


@login_required(login_url='/login/')
def menschen_exam(request):
    class_level = request.GET.get('class_level', None)
    exam_resources = ExamMenschen.objects.filter(exam__class_level=class_level) if class_level else None

    context = {
        'exam_resources': exam_resources,
    }

    return render(request, 'exam_menschen.html', context)


@login_required(login_url='/login/')
def exams_view(request):
    return render(request, 'exam_landing.html', {})
