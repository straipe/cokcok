from django.contrib import admin
from .models import Motion

@admin.register(Motion)
class MotionAdmin(admin.ModelAdmin):
    pass