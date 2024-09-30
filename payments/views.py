from datetime import datetime
from io import BytesIO
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PaymentRecordSerializer
from studentpage.models import Candidate
from .models import PaymentRecord, UniquePayment
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.db.models import Sum


@login_required(login_url='/login/')
def unique_payments(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate
    payments = PaymentRecord.objects.filter(candidate_name=candidate)
    total_amount_paid = sum(payment.amount_paid for payment in payments)

    # Check for a PDF download request
    if 'download' in request.GET and request.GET['download'] == 'pdf':
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

        # Set up the PDF using the specified format
        pdf.setFont("Helvetica", 12)
        pdf.drawString(105, 660, "Ambank House")
        pdf.drawString(105, 640, "00100 CBD, Nairobi")
        pdf.drawString(105, 620, "AG German School Ltd.")
        today_date = datetime.today().strftime('%Y-%m-%d')
        pdf.setFont("Helvetica", 10)
        pdf.drawString(400, 640, f"Date Generated: {today_date}")
        pdf.drawString(400, 620, f"Admission Number: {candidate.admission_number}")
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(105, 580, f"Payment Records for: {candidate.First_Name} {candidate.Last_Name}")

        # Logo and positioning might need to be adjusted
        logo_path = 'C:/Users/Dell/PycharmProjects/agCrm/crmpage/static/img/AG_German_Institute.png'
        pdf.drawImage(logo_path, 400, 700, width=105, height=50, preserveAspectRatio=True)

        # Table Headers
        headers = ["Date of Payment", "Receipt No.", "Payments"]
        y_position = 540  # Adjust the starting y-position for the table
        x_positions = [120, 270, 400]  # Adjust the x-positions for better spacing
        header_height = 550  # Adjust the header height

        # Draw header
        pdf.setFont("Helvetica-Bold", 12)  # Use bold font for headers
        for i, header in enumerate(headers):
            pdf.drawString(x_positions[i], header_height, header)

        # Draw horizontal line below headers
        pdf.line(120, header_height - 5, 480, header_height - 5)

        # Reset font for table content
        pdf.setFont("Helvetica", 11)

        # Fill table rows with payment details
        for payment in payments:
            y_position -= 20  # Adjust the spacing between rows as needed
            payment_date = payment.date_of_payment.strftime('%B %d, %Y')
            payment_receipt = payment.receipt_number
            payment_amount = intcomma(payment.amount_paid)

            # Draw payment details in each cell
            pdf.drawString(x_positions[0], y_position, payment_date)
            pdf.drawString(x_positions[1], y_position, payment_receipt)
            pdf.drawString(x_positions[2], y_position, str(payment_amount))

        formatted_total_amount_paid = intcomma(total_amount_paid)

        # Apply intcomma
        pdf.setFont("Helvetica-Bold", 12)
        pdf.line(105, y_position - 30, 500, y_position - 30)  # Horizontal line
        # Use the formatted total amount
        pdf.drawString(370, y_position - 50, f"Total Paid: {formatted_total_amount_paid} KES")
        pdf.line(105, y_position - 55, 500, y_position - 55)  # Horizontal line
        pdf.line(105, y_position - 60, 500, y_position - 60)  # Second horizontal line

        # Center align the additional information
        center_x = 300  # Adjust as needed
        additional_info_y = y_position - 90
        line_height = 12  # Adjust the line height

        pdf.setFont("Helvetica", 10)

        # Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi
        text = "Akodgan Glaszner German School Ltd. - Ambank House - 00100 CBD, Nairobi"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke
        text = "Phone and WhatsApp +254 110853 892 - info@germaninstitute.co.ke - www.germaninstitute.co.ke"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Bank Details
        text = "Kenya Commercial Bank - Account number 1321761716 or MPESA Paybill: 522 533 Account No: 774 5020"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        # Appreciation
        text = "Thank you for being part of our Institution"
        text_width = pdf.stringWidth(text, "Helvetica", 10)
        pdf.drawString(center_x - text_width / 2, additional_info_y, text)
        additional_info_y -= line_height

        pdf.save()
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        pdf_buffer.close()

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{candidate.First_Name}_payments.pdf"'
        return response

    return render(request, 'unique_payments.html', {
        'candidate': candidate,
        'payments': payments,
        'total_paid': total_amount_paid,
    })


class PaymentRecordCreateAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
