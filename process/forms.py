from django import forms
from .models import Motion_Upload

class MotionUploadForm(forms.ModelForm):
    class Meta:
        model = Motion_Upload
        fields = ['video_file','motion_file']