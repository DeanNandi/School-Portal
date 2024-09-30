from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import SchoolFeeSerializer
from studentpage.models import Candidate
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import SchoolFee
from payments.models import PaymentRecord


class SchoolFeeCreateAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SchoolFeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/login/')
def fee_structures(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if hasattr(request.user, 'candidate'):
        candidate = request.user.candidate

    # Fetch PaymentRecord and SchoolFee objects for the candidate
    payments = PaymentRecord.objects.filter(candidate_name=candidate)
    fees = SchoolFee.objects.filter(candidate=candidate).order_by('starting_month')

    total_amount_paid = sum(payment.amount_paid for payment in payments)

    # Calculate "Payments Made" for each SchoolFee instance
    fees_with_payments = []
    remaining_amount_paid = total_amount_paid  # Copy of total_amount_paid for decrementing
    for fee in fees:
        if remaining_amount_paid > 0:
            payment_for_month = min(remaining_amount_paid, fee.total_amount_to_pay)
            remaining_amount_paid -= payment_for_month
        else:
            payment_for_month = 0  # Set to 0 if remaining_amount_paid is exhausted

        calculated_due_date = fee.get_calculated_due_date()

        fees_with_payments.append({
            'fee': fee,
            'payment_made': payment_for_month,
            'calculated_due_date': calculated_due_date
        })

    return render(request, 'fee_structures.html', {
        'candidate': candidate,
        'payments': payments,
        'fees_with_payments': fees_with_payments,
    })
