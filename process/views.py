import contextlib
import datetime
from accounts.models import Player
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404, JsonResponse
from django.db import connection, transaction
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from .models import Achievement, Motion
from .movenet import process_video
from .serializers import (
    AchievementSerializer,
    AchievementNoPKSerializer,
    MotionSerializer,
)
from storages.backends.s3boto3 import S3Boto3Storage

class PlayerMotionList(APIView,LimitOffsetPagination):
    def get(self, request, pk, format=None):
        try:
            Player.objects.raw(
                f"select * from Player WHERE player_token='{pk}';"
            )
            motions = Motion.objects.filter(player_token=pk)
            motions_paginated = self.paginate_queryset(motions,request)
            serializer = MotionSerializer(motions_paginated, many=True)
            return self.get_paginated_response(serializer.data)
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
        
    def delete(self, request, pk, format=None):
        try:
            Player.objects.raw(
                f"select * from Player WHERE player_token='{pk}';"
            )
            player_token = pk
            with connection.cursor() as cursor:
                cursor.execute(
                    f"delete from Motion where player_token='{player_token}';"
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Player.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def get_limit(self, request):
        if self.limit_query_param:
            with contextlib.suppress(KeyError, ValueError):
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
        return 10

    def get_offset(self, request):
        try:
            return _positive_int(
                request.query_params[self.offset_query_param],
            )
        except (KeyError, ValueError):
            return 0

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'results': data
        })
    
class PlayerMotionDetail(APIView):
    def delete(self, request, pk1, pk2, format=None):
        player_token = pk1
        motion_id = pk2
        try:
            Player.objects.raw(
                f"select * from Player WHERE player_token='{player_token}';"
            )
            with connection.cursor() as cursor:
                cursor.execute(
                    f"delete from Motion where player_token='{player_token}' "\
                    f"and motion_id={motion_id};"
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Player.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AchievementList(APIView):
    def get(self, request, format=None):
        achievements = Achievement.objects.all()
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

def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        return min(ret, cutoff)
    return ret