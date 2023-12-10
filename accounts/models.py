from django.db import models

class Player(models.Model):
    player_token = models.CharField(primary_key=True, max_length=50)
    sex = models.CharField(max_length=1, db_comment='성별')
    years_playing = models.IntegerField(db_comment='구력')
    grade = models.CharField(max_length=10, db_comment='급수')
    handedness = models.CharField(max_length=5, db_comment='주로 쓰는 손')
    email = models.CharField(max_length=100)
    sns = models.CharField(max_length=30)
    created_at = models.DateTimeField(db_comment='가입일')
    is_staff = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'Player'
