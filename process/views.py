import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404
from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Achievement, Motion
from accounts.models import Player
from .movenet import process_video
from .serializers import (
    AchievementSerializer,
    AchievementNoPKSerializer,
    MotionSerializer,
)
from storages.backends.s3boto3 import S3Boto3Storage

class PlayerMotionList(APIView):
    def get_object(self, pk):
        try:
            return Motion.objects.raw(
                f"select * from Motion WHERE player_token='{pk}';"
            )
        except Motion.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk, format=None):
        try:
            Player.objects.raw(
                f"select * from Player WHERE player_token='{pk}';"
            )
            motions = self.get_object(pk)
            serializer = MotionSerializer(motions,many=True)
            return Response(serializer.data)
        except Player.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, pk):
        error_num = 0
        video_url =""
        watch_url =""
        try:
            Player.objects.raw(
                f"select * from Player WHERE player_token='{pk}';"
            )
            upload_video = request.FILES['video_file']
            video_path = default_storage.save(f'videos/{upload_video.name}', upload_video)
            video_url = default_storage.url(video_path)
            player_pose = process_video(video_url)
            pose_strength = ""
            pose_weakness = ""
            if(player_pose[0]<=0.37):
                pose_weakness += "상체 회전이 부족합니다.\n"
            if(player_pose[0]>0.37):
                pose_strength += "적절히 상체를 회전시키고 있습니다.\n"
            if(player_pose[1]<160):
                pose_weakness += "타구 시에 팔을 좀 더 올려야합니다.\n"
            if(player_pose[1]>=160):
                pose_strength += "팔을 적절히 올려 타구하고 있습니다.\n"
            if(player_pose[2]<160):
                pose_weakness += "타구 시에 팔을 좀 더 펴야합니다.\n"
            if(player_pose[2]>=160):
                pose_strength += "팔을 적절히 펴 타구하고 있습니다.\n"
        except MultiValueDictKeyError:
            error_num = error_num + 1
        except Player.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            upload_watch = request.FILES['watch_file']
            watch_path = default_storage.save(f'watches/{upload_watch.name}', upload_watch)
            watch_url = default_storage.url(watch_path)
            # TODO: upload_watch 데이터를 처리할 로직 작성
            wrist_strength = ""
            wrist_weakness = ""
        except MultiValueDictKeyError:
            error_num = error_num + 1
        if(error_num<2):
            player_token = request.data.get('player_token')
            record_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            swing_score = 0
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO Motion(video_url, watch_url, pose_strength, wrist_strength,"\
                    f"pose_weakness, wrist_weakness, player_token, record_date, swing_score) VALUES "\
                    f"('{video_url}','{watch_url}','{pose_strength}','{wrist_strength}','{pose_weakness}',"\
                    f"'{wrist_weakness}','{player_token}',{record_date},{swing_score});"\
                )
            response_data = {}
            response_data['video_url'] = video_url
            response_data['watch_url'] = watch_url
            response_data['pose_strength'] = pose_strength
            response_data['wrist_strength'] = wrist_strength
            response_data['pose_weakness'] = pose_weakness
            response_data['wrist_weakness'] = wrist_weakness
            response_data['player_token'] = player_token
            response_data['record_date'] = record_date
            response_data['swing_score'] = swing_score

            return Response(response_data,status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class AchievementList(APIView):
    def get_object(self):
        try:
            return Achievement.objects.raw(
                f"select * from Achievement;"
            )
        except Achievement.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        achievements = self.get_object()
        serializer = AchievementSerializer(achievements,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer=AchievementNoPKSerializer(
           data=request.data)
        if serializer.is_valid(): #데이터 유효성 검사
            achieve_nm=request.data.get('achieve_nm')
            d_min=request.data.get('d_min')
            c_min=request.data.get('c_min')
            b_min=request.data.get('b_min')
            a_min=request.data.get('a_min')
            s_min=request.data.get('s_min')
            is_month_update=request.data.get('is_month_update')

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Achievement(achieve_nm,d_min,c_min,b_min,a_min,s_min,is_month_update) "\
                        f"VALUES ('{achieve_nm}',{d_min}, "\
                        f"{c_min}, {b_min}, {a_min}, "\
                        f"{s_min}, '{is_month_update}');"
                )
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
