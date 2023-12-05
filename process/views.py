import contextlib
import datetime
import pandas as pd
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
from .core.analysis import SwingAnalysis
from .core.classification import SwingClassification
from .models import (
    Achievement,
    MatchRecord,
    Motion,
    PlayerAchievement
)
#from .movenet import process_video
from .serializers import (
    AchievementSerializer,
    MatchRecordSerializer,
    MotionSerializer,
    PlayerAchievementSerializer,
)
from storages.backends.s3boto3 import S3Boto3Storage

class AchievementList(APIView):
    def get(self, request, format=None):
        achievements = Achievement.objects.all()
        serializer = AchievementSerializer(achievements,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer=AchievementSerializer(
           data=request.data)
        if serializer.is_valid(): #데이터 유효성 검사
            achieve_nm=request.data.get('achieve_nm')
            d_min=request.data.get('d_min')
            c_min=request.data.get('c_min')
            b_min=request.data.get('b_min')
            a_min=request.data.get('a_min')
            s_min=request.data.get('s_min')
            is_month_update=request.data.get('is_month_update')
            icon = request.data.get('icon')

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Achievement "\
                        f"VALUES (NULL,'{achieve_nm}',{d_min}, "\
                        f"{c_min}, {b_min}, {a_min}, "\
                        f"{s_min}, '{is_month_update}','{icon}');"
                )
            return JsonResponse({"message":"업적을 생성하였습니다."})
        return JsonResponse({"message":"형식에 맞지 않은 요청입니다."})

class MatchRecordList(APIView, LimitOffsetPagination):
    def get(self, request, format=None):
        token = get_token(request)
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            try:
                match_id = request.query_params['match_id']
                match = MatchRecord.objects.filter(match_id=match_id)
                serializer = MatchRecordSerializer(match, many=True)
                return Response(serializer.data)
            except MultiValueDictKeyError:
                matches = MatchRecord.objects.filter(player_token=token)
                matches_paginated = self.paginate_queryset(matches,request)
                serializer = MatchRecordSerializer(matches_paginated, many=True)
                return Response(serializer.data)
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})
    
    @transaction.atomic
    def post(self, request):
        token = get_token(request)
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            duration = request.data.get('duration')
            total_distance = request.data.get('total_distance')
            total_energey_burned = request.data.get('total_energey_burned')
            average_heart_rage = request.data.get('average_heart_rage')
            my_score = request.data.get('my_score')
            opponent_score = request.data.get('opponent_score')
            score_history = request.data.get('score_history')
            try:
                upload_watch = request.FILES['watch_file']
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                upload_watch.name = now + '_' + token
                watch_path = default_storage.save(f'match_watch/{upload_watch.name}', upload_watch)
                watch_url = default_storage.url(watch_path)
                watch_csv = pd.read_csv(upload_watch)
                swing_classification = SwingClassification(watch_csv)
                swing_classification.classification()
                swing_analysis_data = swing_classification.classification_result
                print(swing_analysis_data)
            except MultiValueDictKeyError:
                watch_url = ""
            # 12개의 스윙을 JSON 데이터로 반환
            motion_dict = {'bd':0,'bn':0,'bh':0,'bu':0,'fd':0,'fp':0,
                           'fn':0,'fh':0,'fs':0,'fu':0,'ls':0,'ss':0}
            for key in motion_dict.keys():
                pass
            # API 테스트용 더미 데이터
            bd=10;bn=3;bh=8;bu=3;fd=6;fp=2;fn=3;fh=5;fs=2;fu=1;ls=2;ss=5
            total_swing = bd+bn+bh+bu+fd+fp+fn+fh+fs+fu+ls+ss
            player_token = token
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO Match_Record VALUES (NULL, '{start_date}',"\
                    f"'{end_date}','{duration}','{total_distance}','{total_energey_burned}',"\
                    f"'{average_heart_rage}','{my_score}',{opponent_score},{score_history},"\
                    f"{bd},{bn},{bh},{bu},{fd},{fp},{fn},{fh},{fs},{fu},{ls},{ss},"\
                    f"'{watch_url}','{player_token}');"
                )
                #업적1 스윙 횟수 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{total_swing} "\
                    f"WHERE achieve_id=1 and player_token='{token}';"
                )
                #업적2 하이클리어 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{fh} "\
                    f"WHERE achieve_id=2 and player_token='{token}';"
                )
                #업적3 경기 횟수 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+1 "\
                    f"WHERE achieve_id=3 and player_token='{token}';"
                )
                #업적4 경기 시간 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{duration}"\
                    f"WHERE achieve_id=4 and player_token='{token}';"
                )
                #업적5 소모칼로리 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{total_energey_burned}"\
                    f"WHERE achieve_id=5 and player_token='{token}';"
                )

                #모든 업적 ID 불러오기
                cursor.execute(
                    "SELECT achieve_id FROM Achievement;"
                )
                total_achieve_id = cursor.fetchall()

                #등급 업데이트
                for i in range(1,len(total_achieve_id)+1):
                    cursor.execute(
                        f"SELECT cumulative_val FROM Player_Achievement WHERE achieve_id={i} and "\
                        f"player_token = '{token}';"
                    )
                    cumulative_val = cursor.fetchone()

                    cursor.execute(
                        f"SELECT d_min,c_min,b_min,a_min,s_min FROM Achievement WHERE achieve_id={i};"
                    )
                    boundary_val = cursor.fetchall()

                    cursor.execute(
                        "SELECT d_achieve_date,c_achieve_date,b_achieve_date,a_achieve_date,"\
                        f"s_achieve_date FROM Player_Achievement WHERE achieve_id={i} "\
                        f"and player_token='{token}';"
                    )
                    is_update = cursor.fetchall() #승급날짜가 기록되어있는지 여부를 확인

                    # D등급 달성여부 확인
                    if is_update[0][0] is None:
                        if cumulative_val >= boundary_val[0][0]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET d_achieve_date='{now}' "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # C등급 달성여부 확인
                    if is_update[1][0] is None:
                        if cumulative_val >= boundary_val[1][0]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET c_achieve_date='{now}' "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # B등급 달성여부 확인
                    if is_update[2][0] is None:
                        if cumulative_val >= boundary_val[2][0]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET b_achieve_date='{now}' "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # A등급 달성여부 확인
                    if is_update[3][0] is None:
                        if cumulative_val >= boundary_val[3][0]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET a_achieve_date='{now}' "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # S등급 달성여부 확인
                    if is_update[4][0] is None:
                        if cumulative_val >= boundary_val[4][0]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET s_achieve_date='{now}' "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

            response_data = {}
            response_data['start_date'] = start_date
            response_data['end_date'] = end_date
            response_data['duration'] = duration
            response_data['total_distance'] = total_distance
            response_data['total_energey_burned'] = total_energey_burned
            response_data['average_heart_rage'] = average_heart_rage
            response_data['my_score'] = my_score
            response_data['opponent_score'] = opponent_score
            response_data['score_history'] = score_history
            response_data['back_drive'] = bd
            response_data['back_hairpin'] = bn
            response_data['back_high'] = bh
            response_data['back_under'] = bu
            response_data['fore_drive'] = fd
            response_data['fore_drop'] = fp
            response_data['fore_hairpin'] = fn
            response_data['fore_high'] = fh
            response_data['fore_smash'] = fs
            response_data['fore_under'] = fu
            response_data['long_service'] = ls
            response_data['short_service'] = ss
            response_data['watch_url'] = watch_url
            response_data['player_token'] = player_token
            return JsonResponse(response_data)
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})

    def delete(self, request):
        token = get_token(request)
        try:
            match_id = request.query_params['match_id']
            with connection.cursor() as cursor:
                cursor.execute(
                    f"delete from Match_Record where match_id='{match_id}';"
                )
            return JsonResponse({"message":"삭제하였습니다."})
        except MultiValueDictKeyError:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"delete from Match_Record where player_token='{token}';"
                )
            return JsonResponse({"message":"초기화하였습니다."})
            
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

class PlayerAchievementList(APIView):
    def get(self,request):
        token = get_token(request)
        clear = request.query_params['clear']
        player = Player.objects.filter(player_token = token)
        if len(player) != 0:
            if int(clear)==0:
                player_achieve = PlayerAchievement.objects.filter(player_token = token)
                serializer = PlayerAchievementSerializer(player_achieve, many=True)
            else:
                player_achieve = PlayerAchievement.objects.filter(player_token = token,\
                                                                  last_achieve_date__isnull=False)\
                                                                    .order_by('-last_achieve_date')\
                                                                    [:5]
                serializer = PlayerAchievementSerializer(player_achieve, many=True)
            return Response(serializer.data)
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})

class PlayerMotionList(APIView,LimitOffsetPagination):
    def get(self, request, format=None):
        token = get_token(request)
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            try:
                motion_id = request.query_params['motion_id']
                motion = Motion.objects.filter(motion_id=motion_id)
                serializer = MotionSerializer(motion, many=True)
                return Response(serializer.data)
            except MultiValueDictKeyError:
                motions = Motion.objects.filter(player_token=token)
                motions_paginated = self.paginate_queryset(motions,request)
                serializer = MotionSerializer(motions_paginated, many=True)
                return Response(serializer.data)
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})
    
    def post(self, request):
        token = get_token(request)
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            error_num = 0
            video_url =""
            watch_url =""
            try:
                upload_video = request.FILES['video_file']
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                upload_video.name = now + '_' + token
                video_path = default_storage.save(f'videos/{upload_video.name}', upload_video)
                video_url = default_storage.url(video_path)
                player_pose=[1,2,3]
                #player_pose = process_video(video_url)
                pose_score = 0
                if isinstance(player_pose,JsonResponse):
                    return player_pose
                else:
                    pose_strength = ""
                    pose_weakness = ""
                    if(player_pose[0]<=0.37):
                        pose_weakness += "상체 회전이 부족합니다.\n"
                    if(player_pose[0]>0.37):
                        pose_strength += "적절히 상체를 회전시키고 있습니다.\n"
                        pose_score += 20
                    if(player_pose[1]<160):
                        pose_weakness += "타구 시에 팔을 좀 더 올려야합니다.\n"
                    if(player_pose[1]>=160):
                        pose_strength += "팔을 적절히 올려 타구하고 있습니다.\n"
                        pose_score += 40
                    if(player_pose[2]<160):
                        pose_weakness += "타구 시에 팔을 좀 더 펴야합니다.\n"
                    if(player_pose[2]>=160):
                        pose_strength += "팔을 적절히 펴 타구하고 있습니다.\n"
                        pose_score += 40
            except MultiValueDictKeyError:
                error_num = error_num + 1
            
            try:
                upload_watch = request.FILES['watch_file']
                upload_watch.name = now + '_' + token
                watch_path = default_storage.save(f'watches/{upload_watch.name}', upload_watch)
                watch_url = default_storage.url(watch_path)
                watch_csv = pd.read_csv(upload_watch)
                #스윙 분석 실시
                swing_analysis = SwingAnalysis()
                swing_analysis.uploadDataFrame(watch_csv)
                swing_analysis.analysis('fh')
                #테스트 필요
                print(swing_analysis.max)
                print(swing_analysis.score)
                wrist_strength = ""
                wrist_weakness = ""
            except MultiValueDictKeyError:
                error_num = error_num + 1
            if(error_num<2):
                player_token = request.data.get('player_token')
                record_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                wrist_score = max((30000 - swing_analysis.score)/300,0)
                swing_score = (wrist_score + pose_score) / 2
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO Motion VALUES (NULL, '{video_url}',"\
                        f"'{watch_url}','{pose_strength}','{wrist_strength}','{pose_weakness}',"\
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

                return Response(response_data)
            else:
                return JsonResponse({"message":"처리할 데이터가 없습니다."})
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})
        
    def delete(self, request, format=None):
        token = get_token(request)
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            try:
                motion_id = request.query_params['motion_id']
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"delete from Motion where motion_id={motion_id};"
                    )
                return JsonResponse({"message":"삭제하였습니다."})
            except MultiValueDictKeyError:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"delete from Motion where player_token='{token}';"
                    )
                return JsonResponse({"message":"스윙 데이터를 초기화하였습니다."})
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})
        
    def get_limit(self, request):
        if self.limit_query_param:
            with contextlib.suppress(KeyError, ValueError):
                return _positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
        return 5

    def get_offset(self, request):
        try:
            return _positive_int(
                request.query_params[self.offset_query_param],
            )
        except (KeyError, ValueError):
            return 0

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

def get_token(request):
    try:
        return request.META.get('HTTP_AUTHORIZATION').split()[1]
        
    except (KeyError, ValueError):
        return None