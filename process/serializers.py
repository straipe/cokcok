from rest_framework import serializers
from .models import Motion

class MotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = [field.name for field in Motion._meta.get_fields()]

class CodeDetailSerializer(serializers.Serializer):
    detail_code_no = serializers.CharField(min_length=7 ,max_length=7)
    detail_code_nm=serializers.CharField(max_length=50)
    minimum = serializers.IntegerField()
    code_no=serializers.CharField(min_length=5 ,max_length=5)