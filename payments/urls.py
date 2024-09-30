from django.urls import path
from .views import PaymentRecordCreateAPI, unique_payments

urlpatterns = [
    path('api/payment_record/', PaymentRecordCreateAPI.as_view(), name='create_payment_record'),
    path('unique-payment/<int:candidate_id>/', unique_payments, name='unique_payment'),
]
