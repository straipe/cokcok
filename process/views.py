from django.shortcuts import render, redirect
from .forms import SwingUploadForm
from .models import Swing_Upload
from .movenet import process_video
from storages.backends.s3boto3 import S3Boto3Storage

def get_s3_file_url(file):
    if isinstance(file.storage, S3Boto3Storage):
        return file.storage.url(file.name)
    return None

def upload_swing(request):
    if request.method == 'POST':
        form = SwingUploadForm(request.POST, request.FILES)
        if form.is_valid():
            swing = form.save()
            file_url = get_s3_file_url(swing.video_file)
            print(process_video(file_url))
            return redirect("upload_swing")
    else:
        form = SwingUploadForm()
    return render(request,'process/upload_swing.html',{'form':form})

def get_swing_list(request):
    pass

def swing_list(request):
    pass
    # swings = Swing_Upload.objects.all()
    # return render(request, 'process/swing_list.html',{'swings':swings})