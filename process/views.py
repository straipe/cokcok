from django.shortcuts import render, redirect
from django.http import Http404
from .forms import MotionUploadForm
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Motion_Upload, Motion
from .movenet import process_video
from .serializers import MotionSerializer
from storages.backends.s3boto3 import S3Boto3Storage

class UserMotionList(APIView):
    def get_object(self, pk):
        try:
            return Motion.objects.raw(
                f"select * from MOTION WHERE user_id={pk};"
            )
        except Motion.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        motions = self.get_object(pk)
        serializer = MotionSerializer(motions,many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        print(request.data)

def get_s3_file_url(file):
    if isinstance(file.storage, S3Boto3Storage):
        return file.storage.url(file.name)
    return None

def upload_motion(request):
    if request.method == 'POST':
        form = MotionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            motion = form.save()
            file_url = get_s3_file_url(motion.video_file)
            print(process_video(file_url))
            return redirect("upload_motion")
    else:
        form = MotionUploadForm()
    return render(request,'process/upload_motion.html',{'form':form})

def get_motion_list(request):
    pass

def motion_list(request):
    pass
    # swings = Swing_Upload.objects.all()
    # return render(request, 'process/swing_list.html',{'swings':swings})