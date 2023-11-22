from django.contrib import admin
from .models import Motion_Upload

@admin.register(Motion_Upload)
class MotionAdmin(admin.ModelAdmin):
    pass