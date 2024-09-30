from rest_framework import serializers
from .models import SchoolFee


class SchoolFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolFee
        fields = '__all__'
