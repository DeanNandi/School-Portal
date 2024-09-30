from django.urls import path
from .views import SchoolFeeCreateAPI, fee_structures

urlpatterns = [
    path('api/fee_structure/', SchoolFeeCreateAPI.as_view(), name='fee_structure'),
    path('fee/structure/<int:candidate_id>/', fee_structures, name='school_fee'),

]
