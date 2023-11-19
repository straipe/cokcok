from django import forms
from .models import Swing_Upload

class SwingUploadForm(forms.ModelForm):
    class Meta:
        model = Swing_Upload
        fields = ['video_file','motion_file']