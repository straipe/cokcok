import datetime
from django.db import connection, transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Player
from .serializers import PlayerSerializer

class PlayerInfo(APIView):

    def get(self, request, format=None):
        try:
            token = request.META.get('HTTP_AUTHORIZATION').split()[1]
            player = Player.objects.filter(player_token = token)
            if len(player) != 0:
                serializer = PlayerSerializer(player,many=True)
                return JsonResponse(dict(serializer.data[0]))
            else:
                return JsonResponse({"message":"회원가입을 해주세요."})
        except MultiValueDictKeyError:
            return JsonResponse({"message":"잘못된 형식입니다."})
        
    @transaction.atomic    
    def post(self, request):
        request.data['player_token'] = request.META.get('HTTP_AUTHORIZATION').split()[1]
        serializer=PlayerSerializer(data=request.data)
        if serializer.is_valid():
            player_token = request.data.get('player_token')
            sex = request.data.get('sex')
            years_playing = request.data.get('years_playing')
            grade  = request.data.get('grade')
            handedness = request.data.get('handedness')
            email  = request.data.get('email')
            sns = request.data.get('sns')
            with connection.cursor() as cursor:
                cursor.execute(
                        f"INSERT INTO Player values('{player_token}','{sex}','{years_playing}',"\
                        f"'{grade}','{handedness}','{email}','{sns}');"
                )

                # 상시 업적 조회 및 유저와 상시 업적 간 관계 튜플 추가
                cursor.execute(
                    f"SELECT achieve_id from Achievement where is_month_update=0;"
                )
                always_achieve = cursor.fetchall()
                for i in range(len(always_achieve)):
                    cursor.execute(
                        f"INSERT INTO Player_Achievement(player_token,achieve_id) "\
                        f"values ('{player_token}',{always_achieve[i][0]});"
                    )
                
                # 월별 업적 조회 및 유저와 월별 업적 간 관계 튜플 추가
                now = datetime.datetime.now().strftime("%Y-%m-01")
                cursor.execute(
                    f"SELECT achieve_id from Achievement where is_month_update=1;"
                )
                month_achieve = cursor.fetchall()
                for i in range(len(month_achieve)):
                    cursor.execute(
                        f"INSERT INTO Player_Achievement(player_token,achieve_id,achieve_year_month) "\
                        f"values ('{player_token}',{month_achieve[i][0]},'{now}');"
                    )
            return JsonResponse({"message":"회원가입이 완료되었습니다."})
        try:
            if 'player with this player token already exists.' in serializer.errors['player_token']:
                return JsonResponse({"message":"이미 회원가입된 회원입니다."}, status = 400)
            else:
                return JsonResponse({"message":"올바르지 않은 형식입니다."}, status = 400)
        except KeyError:
            return JsonResponse({"message":"토큰이 존재하지 않습니다."}, status = 400)
    
    def put(self, request, format=None):
        request.data['player_token'] = 0
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            player_token = request.META.get('HTTP_AUTHORIZATION').split()[1]
            sex = request.data.get('sex')
            years_playing = request.data.get('years_playing')
            grade  = request.data.get('grade')
            handedness = request.data.get('handedness')
            email  = request.data.get('email')
            sns  = request.data.get('sns')
            with connection.cursor() as cursor:
                cursor.execute(
                        f"UPDATE Player SET sex='{sex}',years_playing={years_playing},"\
                        f"grade='{grade}',handedness='{handedness}',email='{email}',sns='{sns}' "\
                        f"WHERE player_token = '{player_token}';"
                )
            return JsonResponse({"message":"개인정보 수정이 완료되었습니다."})
        return JsonResponse({"message":"올바르지 않은 형식입니다."}, status = 400)
    
    def delete(self,request):
        player_token = request.META.get('HTTP_AUTHORIZATION').split()[1]
        player = Player.objects.filter(player_token = player_token)
        if len(player)!=0:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM Player WHERE player_token='{player_token}';"
                )
            return JsonResponse({"message":"회원탈퇴 되었습니다."})
        return JsonResponse({"message":"회원가입을 해주세요."})