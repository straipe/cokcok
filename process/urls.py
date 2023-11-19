from django.urls import path
from . import views

urlpatterns = [
    path('upload/video/', views.upload_video, name='upload_video'),
    path('upload/motion/', views.upload_motion, name='upload_motion'),
    path('video_list/',views.video_list, name='video_list'),
]