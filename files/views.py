from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PdfMenschen, PdfGrammatik_Aktiv, PracticeMaterial


@login_required(login_url='/login/')
def menschen(request):
    class_level = request.GET.get('class_level', None)
    pdf_resources = PdfMenschen.objects.filter(book__class_level=class_level) if class_level else None

    return render(request, 'files_Menschen.html', {
        'pdf_resources': pdf_resources,

    })


@login_required(login_url='/login/')
def grammar(request):
    class_level = request.GET.get('class_level', None)
    pdf_grammar = PdfGrammatik_Aktiv.objects.filter(book__class_level=class_level) if class_level else None

    return render(request, 'files_grammar.html', {
        'pdf_grammar': pdf_grammar,

    })


@login_required(login_url='/login/')
def practice(request):
    pdf_practice = PracticeMaterial.objects.all()

    return render(request, 'practice_materials.html', {
        'pdf_practice': pdf_practice,

    })


@login_required(login_url='/login/')
def books_view(request):
    return render(request, 'books_landing.html', {})
