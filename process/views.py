import contextlib
from datetime import datetime, timezone, timedelta
import json
import pandas as pd
from accounts.models import Player
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404, JsonResponse
from django.db import connection, transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from sklearn.exceptions import NotFittedError

from .core.analysis import SwingAnalysis
from .core.classification import SwingClassification
from .core.constant import CONST
from .models import (
    Achievement,
    MatchRecord,
    Motion,
    PlayerAchievement,
    SwingScore,
)
from .movenet import process_video
from .serializers import (
    AchievementSerializer,
    MatchRecordSerializer,
    MotionSerializer,
    PlayerAchievementSerializer,
    SwingScoreSerializer
)
from storages.backends.s3boto3 import S3Boto3Storage

class AchievementList(APIView):
    def get(self, request):
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
            unit = request.data.get('unit')
            now = datetime.now().strftime("%Y-%m-01 00:00:00")

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Achievement "\
                        f"VALUES (NULL,'{achieve_nm}',{d_min}, "\
                        f"{c_min}, {b_min}, {a_min}, "\
                        f"{s_min}, '{is_month_update}','{icon}','{unit}');"
                )
                players = Player.objects.all()
                for player in players:
                    token = player.player_token
                    achieves = Achievement.objects.all()
                    for achieve in achieves:
                        player_achieve = PlayerAchievement.objects.filter(player_token=token,achieve_id=achieve.achieve_id)
                        if len(player_achieve) == 0:
                            is_month_update = Achievement.objects.filter(achieve_id=achieve.achieve_id)[0].is_month_update
                            if is_month_update == 0:
                                cursor.execute(
                                    "INSERT INTO Player_Achievement "\
                                        f"VALUES (NULL,'{token}',{achieve.achieve_id}, "\
                                        f"0,NULL,NULL,NULL,NULL,NULL,NULL,NULL);"
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO Player_Achievement "\
                                        f"VALUES (NULL,'{token}',{achieve.achieve_id}, "\
                                        f"0,'{now}',NULL,NULL,NULL,NULL,NULL,NULL);"
                                )

            return JsonResponse({"message":"업적을 생성하였습니다."})
        return JsonResponse({"message":"형식에 맞지 않은 요청입니다."})

class MatchRecordList(APIView, LimitOffsetPagination):
    def get(self, request):
        token = get_token(request)
        #token = '6f5srp1JpUMdRw33TsKW0sc4lfX2'
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            matches = MatchRecord.objects.filter(player_token=token)
            matches_paginated = self.paginate_queryset(matches,request)
            serializer = MatchRecordSerializer(matches_paginated, many=True)
            match_id_set = serializer.data
            for i in range(len(match_id_set)):
                match_id = match_id_set[i]['match_id']
                swings = SwingScore.objects.filter(match_id=match_id)
                match_id_set[i]['swing_list']=[]
                for swing in swings:
                    match_id_set[i]['swing_list'].append({'id':swing.swing_id,'score':swing.score,'type':swing.swing_type})
            return Response(serializer.data)
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})
    
    @transaction.atomic
    def post(self, request):

        def apple_to_korea_time(timestamp):
            apple_watch_epoch = datetime(2001, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            apple_watch_time = apple_watch_epoch + timedelta(seconds=timestamp)
            korea_timezone = timezone(timedelta(hours=9))
            korea_time = apple_watch_time.astimezone(korea_timezone)
            formatted_time = korea_time.strftime("%Y-%m-%d %H:%M:%S")
            return formatted_time
        
        token = get_token(request)
        #token = '6f5srp1JpUMdRw33TsKW0sc4lfX2'
        player = Player.objects.filter(player_token=token)
        #print(request.data)
        if len(player) != 0:
            req_json = request.data.get('metadata_file',None)
            if req_json is not None:
                file_content = req_json.read().decode('utf-8')
                json_data = json.loads(file_content)
                start_date = apple_to_korea_time(float(json_data.get('startDate')))
                end_date = apple_to_korea_time(float(json_data.get('endDate')))
                duration = json_data.get('duration')
                total_distance = json_data.get('totalDistance')
                total_energy_burned = json_data.get('totalEnergyBurned')
                average_heart_rate = json_data.get('averageHeartRate')
                my_score = int(json_data.get('myScore'))
                opponent_score = int(json_data.get('opponentScore'))
                score_history = json_data.get('scoreHistory')
            else:
                return JsonResponse({"message":"Json파일을 보내주세요."})

            upload_watch = request.data.get('watch_file',None)
            if upload_watch is not None:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                upload_watch.name = now + '_' + token
                watch_path = default_storage.save(f'match_watch/{upload_watch.name}', upload_watch)
                watch_url = default_storage.url(watch_path)
                upload_watch.seek(0)
                watch_csv = pd.read_csv(upload_watch)
                swing_list = []
                try:
                    swing_classification = SwingClassification(watch_csv)
                    swing_classification.classification()
                    swing_list = swing_classification.makeAnalysisData()
                except NotFittedError:
                    watch_url = ""
                except AttributeError:
                    watch_url = ""
            else:
                watch_url = ""
            if watch_url is None:
                watch_url = ""
            # 12개의 스윙을 JSON 데이터로 반환
            motion_dict = {'bd':[0,0],'bn':[0,0],'bh':[0,0],'bu':[0,0],'fd':[0,0],'fp':[0,0],
                           'fn':[0,0],'fh':[0,0],'fs':[0,0],'fu':[0,0],'ls':[0,0],'ss':[0,0],
                           'x':[0,0]}
            
            # motion_dict에 각 스트로크에 대한 횟수와 총점 저장
            print(swing_list)
            for key in motion_dict.keys():
                for swing in swing_list:
                    if key == swing[0]:
                        if swing[1] >= 30:
                            motion_dict[key][0] = motion_dict[key][0] + 1
                            motion_dict[key][1] = motion_dict[key][1] + swing[1]
                        else:
                            motion_dict['x'][0] = motion_dict['x'][0] + 1
            #print(motion_dict)
            # motion_dict에 모든 스윙 총점, 횟수 저장
            total_num = 0
            total_score = 0
            swing_average_score = 0
            for key in motion_dict.keys():
                if key != 'x':
                    total_num += motion_dict[key][0]
                    total_score += motion_dict[key][1]
            try:
                swing_average_score = total_score / total_num
            except ZeroDivisionError:
                swing_average_score = 0
            player_token = token
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO Match_Record VALUES (NULL, '{start_date}',"\
                    f"'{end_date}',{duration},{total_distance},{total_energy_burned},"\
                    f"{average_heart_rate},{my_score},{opponent_score},'{score_history}',"\
                    f"'{watch_url}',{swing_average_score},'{player_token}');"
                )
                #날짜 계산
                now_01 = datetime.now().strftime("%Y-%m-01")
                
                #업적1 스윙 횟수 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{total_num} "\
                    f"WHERE achieve_id=1 and player_token='{token}' and '{now_01}'=achieve_year_month;"
                )
                #업적2 하이클리어 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{motion_dict['fh'][0]} "\
                    f"WHERE achieve_id=2 and player_token='{token}';"
                )
                #업적3 경기 횟수 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+1 "\
                    f"WHERE achieve_id=3 and player_token='{token}';"
                )
                #업적4 경기 시간 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{int(duration/60)} "\
                    f"WHERE achieve_id=4 and player_token='{token}';"
                )
                #업적5 소모칼로리 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{total_energy_burned} "\
                    f"WHERE achieve_id=5 and player_token='{token}';"
                )
                #업적6 스매시 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{motion_dict['fs'][0]} "\
                    f"WHERE achieve_id=6 and player_token='{token}';"
                )
                #업적7 드라이브 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{motion_dict['fd'][0]+motion_dict['bd'][0]} "\
                    f"WHERE achieve_id=7 and player_token='{token}';"
                )
                #업적8 이동거리 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{total_distance} "\
                    f"WHERE achieve_id=8 and player_token='{token}' and '{now_01}'=achieve_year_month;"
                )
                #업적9 언더클리어 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{motion_dict['bu'][0]+motion_dict['fu'][0]} "\
                    f"WHERE achieve_id=9 and player_token='{token}' and '{now_01}'=achieve_year_month;"
                )
                #업적10 헤어핀 누적치 업데이트
                cursor.execute(
                    f"UPDATE Player_Achievement SET cumulative_val=cumulative_val+{motion_dict['bn'][0]+motion_dict['fn'][0]} "\
                    f"WHERE achieve_id=10 and player_token='{token}' and '{now_01}'=achieve_year_month;"
                )

                #12개의 스트로크 평균점수, 타입 저장
                cursor.execute(
                    f"SELECT match_id FROM Match_Record WHERE start_date='{start_date}'and "\
                    f"player_token='{player_token}';"
                )
                last_match_id = int(cursor.fetchone()[0])
                for id, swing in enumerate(swing_list):
                    if swing[1] >= 30:
                        cursor.execute(
                            f"INSERT INTO Swing_Score VALUES (NULL,{id+1},{swing[1]},'{swing[0]}',"\
                            f"{last_match_id});"
                        )
                    else:
                        cursor.execute(
                            f"INSERT INTO Swing_Score VALUES (NULL,{id+1},0,'x',"\
                            f"{last_match_id});"
                        )
                
                #모든 업적 ID 불러오기
                total_achieve_num = PlayerAchievement.objects.filter(Q(player_token=token) &
                                                                     (Q(achieve_year_month__isnull=True)\
                                                                       | Q(achieve_year_month=now_01))
                                                                     )

                #등급 업데이트
                for i in range(1,len(total_achieve_num)+1):
                    cursor.execute(
                        f"SELECT cumulative_val FROM Player_Achievement WHERE achieve_id={i} and "\
                        f"player_token='{token}';"
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
                        if cumulative_val[0] >= boundary_val[0][0]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET d_achieve_date='{now}', "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # C등급 달성여부 확인
                    if is_update[0][1] is None:
                        if cumulative_val[0] >= boundary_val[0][1]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET c_achieve_date='{now}', "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # B등급 달성여부 확인
                    if is_update[0][2] is None:
                        if cumulative_val[0] >= boundary_val[0][2]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET b_achieve_date='{now}', "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # A등급 달성여부 확인
                    if is_update[0][3] is None:
                        if cumulative_val[0] >= boundary_val[0][3]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET a_achieve_date='{now}', "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )

                    # S등급 달성여부 확인
                    if is_update[0][4] is None:
                        if cumulative_val[0] >= boundary_val[0][4]:
                            cursor.execute(
                                f"UPDATE Player_Achievement SET s_achieve_date='{now}', "\
                                f"last_achieve_date='{now}' "\
                                f"WHERE achieve_id={i} and player_token='{token}';"
                            )
            return JsonResponse({"message":"경기 기록이 성공적으로 업로드 되었습니다."})
        else:
            return JsonResponse({"error":"회원가입을 해주세요."})


    def delete(self, request):
        token = get_token(request)
        match_id = request.data.get('match_id',None)
        if match_id is not None:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"delete from Match_Record where match_id='{match_id}' and player_token='{token}';"
                )
            return JsonResponse({"message":"삭제하였습니다."})
        else:
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
            upload_video = request.data.get('video_file',None)
            if upload_video is not None:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                upload_video.name = now + '_' + token[1] + '.mp4'
                video_path = default_storage.save(f'videos/{upload_video.name}', upload_video)
                video_url = default_storage.url(video_path)
                player_pose = process_video(video_url)
                #player_pose = [1,2,3]
                if isinstance(player_pose,JsonResponse):
                    return player_pose
                else:
                    pose_strength = ""
                    pose_weakness = ""
                    pose_score = 0
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
            else:
                error_num = error_num + 1
            
            upload_watch = request.data.get('watch_file',None)
            if upload_watch is not None:
                upload_watch.name = now + '_' + token[1] + '.csv'
                watch_path = default_storage.save(f'watches/{upload_watch.name}', upload_watch)
                watch_url = default_storage.url(watch_path)
                upload_watch.seek(0)
                watch_csv = pd.read_csv(upload_watch)
                #스윙 분석 실시
                swing_analysis = SwingAnalysis(watch_csv)
                swing_analysis.analysis('fh')
                #테스트 필요
                print(swing_analysis.score)
                swing_analysis.interpret()
                wrist_strength = ""
                wrist_weakness = ""
                #스윙 피드백 리스트
                swing_feedback_dict = CONST.SWING_INTERPRET_RES

                for key in swing_analysis.feedback:
                    if int(key)>=500:
                        wrist_strength += swing_feedback_dict[key]+"\n"
                    else:
                        wrist_weakness += swing_feedback_dict[key]+"\n"
            else:
                error_num = error_num + 1

            if(error_num<2):
                player_token = token
                record_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                wrist_score = max((3 - swing_analysis.score)*100/3,0)
                swing_score = int((wrist_score + pose_score) / 2)
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO Motion VALUES (NULL, '{video_url}',"\
                        f"'{watch_url}','{pose_strength}','{wrist_strength}','{pose_weakness}',"\
                        f"'{wrist_weakness}','{player_token}','{record_date}',{swing_score});"\
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
                response_data['res'] = swing_analysis.res
                response_data['res_prepare'] = swing_analysis.res_prepare
                response_data['res_impact'] = swing_analysis.res_impact
                response_data['res_follow'] = swing_analysis.res_follow
                response_data['wrist_max_acc'] = swing_analysis.res_max
                return Response(response_data)
            else:
                return JsonResponse({"message":"처리할 데이터가 없습니다."})
        else:
            return JsonResponse({"message":"회원가입을 해주세요."})
        
    def delete(self, request, format=None):
        token = get_token(request)
        player = Player.objects.filter(player_token=token)
        if len(player) != 0:
            motion_id = request.data.get('motion_id',None)
            if motion_id is not None:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"delete from Motion where motion_id={motion_id} and player_token='{token}';"
                    )
                return JsonResponse({"message":"삭제하였습니다."})
            else:
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