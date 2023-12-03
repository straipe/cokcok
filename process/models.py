from django.db import models

class Motion(models.Model):
    motion_id = models.AutoField(primary_key=True, db_comment='데이터 아이디')
    video_url = models.CharField(max_length=200, blank=True, null=True, db_comment='영상 storage URL')
    watch_url = models.CharField(max_length=200, blank=True, null=True, db_comment='워치 storage URL')
    pose_strength = models.CharField(max_length=100, blank=True, null=True, db_comment='자세 장점')
    wrist_strength = models.CharField(max_length=100, blank=True, null=True, db_comment='손목 활용 장점')
    pose_weakness = models.CharField(max_length=100, blank=True, null=True, db_comment='자세 단점')
    wrist_weakness = models.CharField(max_length=100, blank=True, null=True, db_comment='손목 활용 단점')
    player_token = models.CharField(max_length=50)
    record_date = models.DateField(db_comment='측정 날짜')
    swing_score = models.IntegerField(db_comment='스윙 총점')

    class Meta:
        managed = False
        db_table = 'Motion'


class MatchRecord(models.Model):
    match_id = models.AutoField(primary_key=True, db_comment='경기 아이디')
    start_date = models.DateField(db_comment='시작날짜')
    end_date = models.DateField(db_comment='종료날짜')
    duration = models.IntegerField(db_comment='경기시간')
    total_distance = models.FloatField(db_comment='뛴거리')
    total_energey_burned = models.FloatField(db_comment='칼로리소모량')
    average_heart_rage = models.FloatField(db_comment='평균심박수')
    my_score = models.IntegerField(db_comment='내점수')
    opponent_score = models.IntegerField(db_comment='상대점수')
    score_history = models.CharField(max_length=100, db_comment='히스토리')
    forehand_overarm = models.IntegerField(blank=True, null=True, db_comment='fo 횟수')
    forehand_underarm = models.IntegerField(blank=True, null=True, db_comment='fu 횟수')
    backhand_overarm = models.IntegerField(blank=True, null=True, db_comment='bo 횟수')
    backhand_underarm = models.IntegerField(blank=True, null=True, db_comment='bu 횟수')
    forehand_smash = models.IntegerField(blank=True, null=True, db_comment='fs 횟수')
    watch_url = models.CharField(max_length=200, blank=True, null=True, db_comment='워치 데이터 URL')
    player_token = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Match_Record'


class Achievement(models.Model):
    achieve_id = models.AutoField(primary_key=True, db_comment='업적 아이디')
    achieve_nm = models.CharField(max_length=50, db_comment='업적 이름')
    d_min = models.IntegerField(db_comment='D등급 최솟값')
    c_min = models.IntegerField(db_comment='C등급 최솟값')
    b_min = models.IntegerField(db_comment='B등급 최솟값')
    a_min = models.IntegerField(db_comment='A등급 최솟값')
    s_min = models.IntegerField(db_comment='S등급 최솟값')
    is_month_update = models.CharField(max_length=1, db_comment='매월갱신여부')
    icon = models.CharField(max_length=100, db_comment='아이콘')

    class Meta:
        managed = False
        db_table = 'Achievement'


class PlayerAchievement(models.Model):
    relation_id = models.AutoField(primary_key=True, db_comment='관계 아이디')
    player_token = models.CharField(max_length=50)
    achieve = models.IntegerField(db_comment='업적 아이디')
    cumulative_val = models.IntegerField(blank=True, null=True, db_comment='누적치')
    achieve_year_month = models.DateField(blank=True, null=True, db_comment='업적년월')
    d_achieve_date = models.DateField(blank=True, null=True, db_comment='D등급 달성일자')
    c_achieve_date = models.DateField(blank=True, null=True, db_comment='C등급 달성일자')
    b_achieve_date = models.DateField(blank=True, null=True, db_comment='B등급 달성일자')
    a_achieve_date = models.DateField(blank=True, null=True, db_comment='A등급 달성일자')
    s_achieve_date = models.DateField(blank=True, null=True, db_comment='S등급 달성일자')
    last_achieve_date = models.DateField(blank=True, null=True, db_comment='최근 달성일자')

    class Meta:
        managed = False
        db_table = 'Player_Achievement'
