# Generated by Django 4.2.7 on 2023-11-27 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("process", "0002_motion"),
    ]

    operations = [
        migrations.CreateModel(
            name="Achievement",
            fields=[
                (
                    "achieve_id",
                    models.AutoField(
                        db_comment="업적 아이디", primary_key=True, serialize=False
                    ),
                ),
                ("achieve_nm", models.CharField(db_comment="업적 이름", max_length=50)),
                ("d_min", models.IntegerField(db_comment="D등급 최솟값")),
                ("c_min", models.IntegerField(db_comment="C등급 최솟값")),
                ("b_min", models.IntegerField(db_comment="B등급 최솟값")),
                ("a_min", models.IntegerField(db_comment="A등급 최솟값")),
                ("s_min", models.IntegerField(db_comment="S등급 최솟값")),
                (
                    "is_month_update",
                    models.CharField(db_comment="매월갱신여부", max_length=1),
                ),
            ],
            options={
                "db_table": "ACHIEVEMENT",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="MatchRecord",
            fields=[
                (
                    "match_id",
                    models.AutoField(
                        db_comment="경기 아이디", primary_key=True, serialize=False
                    ),
                ),
                ("start_date", models.DateField(db_comment="시작날짜")),
                ("end_date", models.DateField(db_comment="종료날짜")),
                ("duration", models.IntegerField(db_comment="경기시간")),
                ("total_distance", models.FloatField(db_comment="뛴거리")),
                ("total_energey_burned", models.FloatField(db_comment="칼로리소모량")),
                ("average_heart_rage", models.FloatField(db_comment="평균심박수")),
                ("my_score", models.IntegerField(db_comment="내점수")),
                ("opponent_score", models.IntegerField(db_comment="상대점수")),
                (
                    "my_score_history",
                    models.CharField(db_comment="내점수 히스토리", max_length=100),
                ),
                (
                    "opponent_score_history",
                    models.CharField(db_comment="상대점수 히스토리", max_length=100),
                ),
                (
                    "forehand_overarm",
                    models.IntegerField(blank=True, db_comment="fo 횟수", null=True),
                ),
                (
                    "forehand_underarm",
                    models.IntegerField(blank=True, db_comment="fu 횟수", null=True),
                ),
                (
                    "backhand_overarm",
                    models.IntegerField(blank=True, db_comment="bo 횟수", null=True),
                ),
                (
                    "backhand_underarm",
                    models.IntegerField(blank=True, db_comment="bu 횟수", null=True),
                ),
                (
                    "forehand_smash",
                    models.IntegerField(blank=True, db_comment="fs 횟수", null=True),
                ),
                (
                    "watch_url",
                    models.CharField(
                        blank=True, db_comment="워치 데이터 URL", max_length=200, null=True
                    ),
                ),
                ("user", models.IntegerField()),
            ],
            options={
                "db_table": "MATCH_RECORD",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="UserAchievement",
            fields=[
                (
                    "relation_id",
                    models.AutoField(
                        db_comment="관계 아이디", primary_key=True, serialize=False
                    ),
                ),
                ("user", models.IntegerField(db_comment="유저 아이디")),
                (
                    "cumulative_val",
                    models.IntegerField(blank=True, db_comment="누적치", null=True),
                ),
                (
                    "achieve_year_month",
                    models.DateField(blank=True, db_comment="업적년월", null=True),
                ),
                (
                    "d_achieve_date",
                    models.DateField(blank=True, db_comment="D등급 달성일자", null=True),
                ),
                (
                    "c_achieve_date",
                    models.DateField(blank=True, db_comment="C등급 달성일자", null=True),
                ),
                (
                    "b_achieve_date",
                    models.DateField(blank=True, db_comment="B등급 달성일자", null=True),
                ),
                (
                    "a_achieve_date",
                    models.DateField(blank=True, db_comment="A등급 달성일자", null=True),
                ),
                (
                    "s_achieve_date",
                    models.DateField(blank=True, db_comment="S등급 달성일자", null=True),
                ),
            ],
            options={
                "db_table": "USER_ACHIEVEMENT",
                "managed": False,
            },
        ),
        migrations.DeleteModel(
            name="Video",
        ),
        migrations.AlterModelOptions(
            name="motion",
            options={"managed": False},
        ),
    ]