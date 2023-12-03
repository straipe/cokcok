from rest_framework import serializers
from .models import Achievement, MatchRecord, Motion, PlayerAchievement

class AchievementSerializer(serializers.ModelSerializer):
     class Meta:
        model = Achievement
        fields = [field.name for field in Achievement._meta.get_fields()]

class MatchRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchRecord
        fields = [field.name for field in MatchRecord._meta.get_fields()]

class MotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Motion
        fields = [field.name for field in Motion._meta.get_fields()]

class PlayerAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerAchievement
        fields = [field.name for field in PlayerAchievement._meta.get_fields()]