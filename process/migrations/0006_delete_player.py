# Generated by Django 4.2.7 on 2023-11-30 02:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("process", "0005_player_playerachievement_delete_user_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Player",
        ),
    ]
