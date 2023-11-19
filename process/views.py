from django.shortcuts import render, redirect
from .forms import VideoForm, MotionForm
from .models import Video
from .movenet import process_video
from storages.backends.s3boto3 import S3Boto3Storage

def get_s3_file_url(file):
    if isinstance(file.storage, S3Boto3Storage):
        return file.storage.url(file.name)
    return None

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            file_url = get_s3_file_url(video.video_file)
            print(process_video(file_url))
            return redirect("upload_video")
    else:
        form = VideoForm()
    return render(request,'process/upload_video.html',{'form':form})

def upload_motion(request):
    if request.method == 'POST':
        form = MotionForm(request.POST, request.FILES)
        if form.is_valid():
            motion = form.save()
            file_url = get_s3_file_url(motion.motion_file)
            
            return redirect("upload_motion")
    else:
        form = MotionForm()
    return render(request,'process/upload_motion.html',{'form':form})

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'process/video_list.html',{'videos':videos})