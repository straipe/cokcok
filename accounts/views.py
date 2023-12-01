import datetime
from django.db import connection, transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Player
from .serializers import PlayerSerializer

class PlayerInfo(APIView):

    def get_object(self, pk):
        try:
            return Player.objects.raw(
                    f"select * from Player WHERE player_token='{pk}';"
                )
        except Player.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        player_info = self.get_object(pk)
        serializer = PlayerSerializer(player_info,many=True)
        return Response(serializer.data)
        
    def post(self, request, pk):
        serializer=PlayerSerializer(data=request.data)
        if serializer.is_valid():
            player_token = pk
            sex = request.data.get('sex')
            years_playing = request.data.get('years_playing')
            grade  = request.data.get('grade')
            handedness = request.data.get('handedness')
            email  = request.data.get('email')
            with connection.cursor() as cursor:
                cursor.execute(
                        f"INSERT INTO Player values('{player_token}','{sex}','{years_playing}',"\
                        f"'{grade}','{handedness}','{email}');"
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


            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk, format=None):
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            player_token = pk
            sex = request.data.get('sex')
            years_playing = request.data.get('years_playing')
            grade  = request.data.get('grade')
            handedness = request.data.get('handedness')
            email  = request.data.get('email')
            with connection.cursor() as cursor:
                cursor.execute(
                        f"UPDATE Player SET sex='{sex}',years_playing={years_playing},"\
                        f"grade='{grade}',handedness='{handedness}',email='{email}' "\
                        f"WHERE player_token = '{player_token}';"
                )
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk,format=None):
        with connection.cursor() as cursor:
                cursor.execute(
                   f"DELETE FROM Player WHERE player_token='{pk}';"
                )
        return Response(status=status.HTTP_204_NO_CONTENT)
