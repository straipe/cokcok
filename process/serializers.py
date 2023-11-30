from rest_framework import serializers
from .models import Achievement, Motion, Player

class MotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = [field.name for field in Motion._meta.get_fields()]

class MotionPostSerializer(serializers.Serializer):
    video_url = serializers.CharField(max_length=200)
    motion_url = serializers.CharField(max_length=200)
    pose_strength = serializers.CharField(max_length=100)
    wrist_strength = serializers.CharField(max_length=100)
    pose_weakness = serializers.CharField(max_length=100)
    wrist_weakness = serializers.CharField(max_length=100)
    player_token = serializers.IntegerField()
    record_date = serializers.DateTimeField()

class AchievementSerializer(serializers.ModelSerializer):
     class Meta:
        model = Achievement
        fields = [field.name for field in Achievement._meta.get_fields()]

class AchievementNoPKSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        exclude = ('achieve_id')

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [field.name for field in Player._meta.get_fields()]
