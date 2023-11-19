from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')

class Motion(models.Model):
    title = models.CharField(max_length=100)
    motion_file = models.FileField(upload_to='motions/')