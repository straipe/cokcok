from django import forms
from .models import Motion

class MotionUploadForm(forms.ModelForm):
    class Meta:
        model = Motion
        fields = ['video_file','motion_file']