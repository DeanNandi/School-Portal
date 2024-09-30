from .models import PdfMenschen


def add_pdfmenschen_to_context(request):
    pdfmenschen = None
    if request.user.is_authenticated:
        try:
            pdfmenschen = PdfMenschen.objects.all
        except PdfMenschen.DoesNotExist:
            pdfmenschen = None
    return {'pdfmenschen': pdfmenschen}
