from django import forms
from .models import Video, Motion

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']

class MotionForm(forms.ModelForm):
    class Meta:
        model = Motion
        fields = ['title', 'motion_file']