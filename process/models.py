from django.db import models

class Motion_Upload(models.Model):
    video_file = models.FileField(upload_to='videos/',blank=True)
    motion_file = models.FileField(upload_to='motions/',blank=True)

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=36, db_comment='유저 아이디')
    sex = models.CharField(max_length=1, db_comment='성별')
    years_playing = models.IntegerField(db_comment='구력')
    grade = models.CharField(max_length=10, db_comment='급수')
    handedness = models.CharField(max_length=5, db_comment='주로 쓰는 손')
    swing_cnt = models.IntegerField(db_comment='이번달 스윙 횟수')
    swing_grade = models.CharField(max_length=7, db_comment='이번달 스윙 등급')
    match_cnt = models.IntegerField(db_comment='이번달 경기 횟수')
    match_cnt_grade = models.CharField(max_length=7, db_comment='이번달 경기 횟수 등급')
    match_time = models.IntegerField(db_comment='이번달 경기 시간')
    match_time_grade = models.CharField(max_length=7, db_comment='이번달 경기 시간 등급')

    class Meta:
        managed = False
        db_table = 'USER'


class Motion(models.Model):
    motion_id = models.AutoField(primary_key=True, db_comment='데이터 아이디')
    video_url = models.CharField(max_length=200, blank=True, null=True, db_comment='영상 데이터 URL')
    watch_url = models.CharField(max_length=200, blank=True, null=True, db_comment='워치 데이터 URL')
    pose_strength = models.CharField(max_length=100, blank=True, null=True, db_comment='자세 장점')
    wrist_strength = models.CharField(max_length=100, blank=True, null=True, db_comment='손목 활용 장점')
    pose_weakness = models.CharField(max_length=100, blank=True, null=True, db_comment='자세 단점')
    wrist_weakness = models.CharField(max_length=100, blank=True, null=True, db_comment='손목 활용 단점')
    user = models.ForeignKey(User, models.DO_NOTHING, db_comment='유저 아이디')
    record_date = models.DateField(db_comment='측정 날짜')
    swing_score = models.IntegerField(db_comment='스윙 총점')

    class Meta:
        managed = False
        db_table = 'MOTION'


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
    my_score_history = models.CharField(max_length=100, db_comment='내점수 히스토리')
    opponent_score_history = models.CharField(max_length=100, db_comment='상대점수 히스토리')
    forehand_overarm = models.IntegerField(blank=True, null=True, db_comment='fo 횟수')
    forehand_underarm = models.IntegerField(blank=True, null=True, db_comment='fu 횟수')
    backhand_overarm = models.IntegerField(blank=True, null=True, db_comment='bo 횟수')
    backhand_underarm = models.IntegerField(blank=True, null=True, db_comment='bu 횟수')
    forehand_smash = models.IntegerField(blank=True, null=True, db_comment='fs 횟수')
    watch_url = models.CharField(max_length=200, blank=True, null=True, db_comment='워치 데이터 URL')
    user = models.ForeignKey(User, models.DO_NOTHING, db_comment='유저 아이디')

    class Meta:
        managed = False
        db_table = 'MATCH_RECORD'


class CodeDivision(models.Model):
    code_no = models.CharField(primary_key=True, max_length=5, db_comment='코드 번호')
    code_nm = models.CharField(max_length=50, db_comment='코드 이름')

    class Meta:
        managed = False
        db_table = 'CODE_DIVISION'


class CodeDetail(models.Model):
    detail_code_no = models.CharField(primary_key=True, max_length=7, db_comment='상세 코드 번호')
    detail_code_nm = models.CharField(max_length=50, db_comment='상세 코드 이름')
    minimum = models.IntegerField(blank=True, null=True, db_comment='최솟값')
    code_no = models.ForeignKey(CodeDivision, models.DO_NOTHING, db_column='code_no', db_comment='코드 번호')

    class Meta:
        managed = False
        db_table = 'CODE_DETAIL'