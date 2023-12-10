from accounts.models import Player
from datetime import datetime
from django.db import connection
from .models import Achievement

def hello_every_minute():
    print('hello')

def update_every_month():
    now = datetime.now().strftime("%Y-%m-01 00:00:00")
    #매월 갱신 업적에 대한 갱신 수행
    with connection.cursor() as cursor:
        players = Player.objects.all()
        need_update_achieves = Achievement.objects.filter(is_month_update='1')
        for player in players:
            token = player.player_token
            for achieve in need_update_achieves:
                achieve_id = achieve.achieve_id
                cursor.execute(
                    "INSERT INTO Player_Achievement "\
                    f"VALUES (NULL,'{token}',{achieve_id}, "\
                    f"0,'{now}',NULL,NULL,NULL,NULL,NULL,NULL);"
                )
